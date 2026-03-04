"""
Jarvis AI — Async Input Handler

Mevcut handler.py'nin async karşılığı.
FastAPI (Server/app.py) tarafından çağrılır.

Tasarım kararları:
  - Router (Brain/router.py) sync kalır → I/O yok, pure keyword matching
  - Ollama çağrıları → ollama.AsyncClient ile async
  - Mevcut Skills → asyncio.to_thread() ile sarmalanır (blocking I/O)
  - Mevcut handler.py'ye DOKUNULMAZ → CLI/GUI geriye uyumluluk
"""

import asyncio
import json
from typing import Any, Optional

import ollama as ollama_sync

from Brain.router import classify_intent
from Brain.memory import Memory
from Skills.skills_manager import perform_skill
from logging_config import get_logger
from settings import JarvisSettings

logger = get_logger("core.async_handler")

# Skill çalıştırılmayan aksiyonlar
_NON_SKILL_ACTIONS: frozenset[str] = frozenset({
    "small_talk", "unknown", "missing_parameters", "multi_action"
})

# Dosya/klasör işlemleri
_FILE_ACTIONS: frozenset[str] = frozenset({
    "create_file", "create_folder", "delete_file", "delete_folder",
    "write_to_file", "list_dir", "read_file", "list_dir_recursive",
})


# ── Ana Async Orkestratör ──────────────────────────────────


async def process_input_async(
    user_input: str,
    memory: Memory,
    user_id: str,
    settings: JarvisSettings,
) -> dict[str, Any]:
    """
    Ana async orkestratör — FastAPI endpoint'i tarafından çağrılır.

    Akış:
        1. Presence check (sync, hızlı)
        2. Pending parametre kontrolü (sync, hızlı)
        3. Router ile intent sınıflandırma (sync, hızlı)
        4. Uygun async engine'e yönlendirme

    Args:
        user_input: Kullanıcı mesajı
        memory: Kullanıcıya özel Memory instance
        user_id: Kullanıcı tanımlayıcısı
        settings: Uygulama ayarları

    Returns:
        {"response": str, "action_taken": str | None}
    """
    # Presence check
    normalized: str = user_input.lower().strip()
    presence_triggers = (
        "jarvis orda mısın", "jarvis orada mısın",
        "hey jarvis orda mısın", "hey jarvis orada mısın",
    )
    if any(trigger in normalized for trigger in presence_triggers):
        return {
            "response": "Sizin için her zaman buradayım Efendim.",
            "action_taken": "presence",
        }

    # Pending parametre kontrolü
    if memory.has_pending():
        completed = memory.fill_pending(user_input)
        if completed:
            action = completed["action"]
            params = completed["params"]
            # Skill'i thread'de çalıştır (blocking I/O)
            skill_result = await asyncio.to_thread(perform_skill, action, params)
            memory.clear_pending()
            reply = "İşleminiz tamamlandı Efendim." if skill_result else "İşlem başarısız oldu Efendim."
            return {"response": reply, "action_taken": action}

        # Hala eksik parametre var
        next_param = memory.pending_params[0] if memory.pending_params else "parametre"
        return {
            "response": f"{next_param} nedir Efendim?",
            "action_taken": "missing_parameters",
        }

    # Router — sync (keyword matching, I/O yok)
    route: str = classify_intent(user_input)
    logger.info("intent_classified", user_id=user_id, route=route)

    if route == "coding":
        return await _handle_coding_async(user_input, memory, settings)

    if route == "reasoning":
        return await _handle_reasoning_async(user_input, memory, settings)

    # fast → Intent Engine
    return await _handle_fast_model_async(user_input, memory, settings)


# ── Async Engine Handlers ──────────────────────────────────


async def _handle_fast_model_async(
    user_input: str,
    memory: Memory,
    settings: JarvisSettings,
) -> dict[str, Any]:
    """
    Intent Engine ile komutu async olarak işle.
    Ollama AsyncClient kullanır.
    """
    client = ollama_sync.AsyncClient(host=settings.ollama_base_url)

    # System prompt'u import et (mevcut intent_engine'den)
    from Brain.intent_engine import SYSTEM_PROMPT, _DEFAULT_FIELDS

    history_msgs: list[dict] = []
    for entry in memory.get_history()[-3:]:
        history_msgs.append({"role": "user", "content": entry.get("user", "")})
        history_msgs.append({"role": "assistant", "content": entry.get("jarvis", "")})

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history_msgs,
        {"role": "user", "content": user_input},
    ]

    try:
        response = await client.chat(
            model=settings.fast_model,
            messages=messages,
            format="json",
            options={"temperature": 0.0},
        )

        result: dict = json.loads(response.message.content)
        for key, default_value in _DEFAULT_FIELDS.items():
            result.setdefault(key, default_value)

        intent_type: str = result.get("type", "skill")
        action: str = result.get("action", "unknown")
        reply: str = result.get("reply", "Efendim?")

        logger.info(
            "intent_parsed",
            type=intent_type,
            action=action,
            confidence=result.get("confidence", 0.0),
        )

        # type="coding" veya "reasoning" → ilgili engine'e yönlendir
        if intent_type == "coding":
            return await _handle_coding_async(user_input, memory, settings)
        if intent_type == "reasoning":
            return await _handle_reasoning_async(user_input, memory, settings)

        # Parametreleri hazırla
        parameters: dict = result.get("parameters", {})
        if not isinstance(parameters, dict):
            parameters = {}

        for key in ("path", "name", "song_name", "query"):
            value = result.get(key)
            if value:
                parameters[key] = value

        if action in _FILE_ACTIONS and not parameters.get("path"):
            parameters["path"] = "desktop"

        # Skill çalıştır
        if action not in _NON_SKILL_ACTIONS:
            await asyncio.to_thread(perform_skill, action, parameters)

        memory.add(user_input, reply)

        return {"response": reply, "action_taken": action}

    except json.JSONDecodeError as exc:
        logger.error("json_parse_error", error=str(exc))
    except Exception as exc:
        logger.error("fast_model_error", error=str(exc), exc_info=True)

    return {
        "response": "Bir hata oluştu Efendim.",
        "action_taken": "error",
    }


async def _handle_reasoning_async(
    user_input: str,
    memory: Memory,
    settings: JarvisSettings,
) -> dict[str, Any]:
    """
    Reasoning Engine async handler.
    Ollama AsyncClient ile karmaşık istekleri işler.
    """
    client = ollama_sync.AsyncClient(host=settings.ollama_base_url)

    from Brain.reasoning_engine import (
        REASONING_SYSTEM_PROMPT,
        _DEFAULT_RESULT_FIELDS,
        format_reasoning_response,
    )

    try:
        response = await client.chat(
            model=settings.reasoning_model,
            messages=[
                {"role": "system", "content": REASONING_SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            format="json",
            options={"temperature": settings.reasoning_temperature},
        )

        result: dict = json.loads(response.message.content)
        result["success"] = True

        for key, default_value in _DEFAULT_RESULT_FIELDS.items():
            result.setdefault(key, default_value)

        response_text = format_reasoning_response(result)

        # Çalıştırılabilir adımlar (plan executor)
        executable_steps = result.get("executable_steps")
        if executable_steps and isinstance(executable_steps, list):
            from Brain.plan_executor import execute_plan, format_execution_result

            execution_result = await asyncio.to_thread(execute_plan, executable_steps)
            execution_message = format_execution_result(execution_result)
            if execution_message:
                response_text += f"\n\n{execution_message}"

        memory.add(user_input, response_text)

        return {
            "response": response_text,
            "action_taken": result.get("type", "reasoning"),
        }

    except Exception as exc:
        logger.error("reasoning_error", error=str(exc), exc_info=True)
        return {
            "response": "Düşünme sürecinde bir hata oluştu Efendim.",
            "action_taken": "error",
        }


async def _handle_coding_async(
    user_input: str,
    memory: Memory,
    settings: JarvisSettings,
) -> dict[str, Any]:
    """
    Coding Engine async handler.
    Mevcut sync coding_engine'i thread'de çalıştırır
    (coding_engine karmaşık agentic loop içerdiğinden tam async dönüşümü sonraya bırakıldı).
    """
    from Brain.coding_engine import process_coding_task

    try:
        result = await asyncio.to_thread(
            process_coding_task,
            user_input=user_input,
            confirm_fn=lambda tool, name, preview: True,
        )

        response = result.get("response", "İşlem tamamlandı Efendim.")
        actions = result.get("actions_taken", [])

        if actions:
            logger.info(
                "coding_complete",
                tool_calls=len(actions),
                tools=", ".join(a.get("tool", "?") for a in actions),
            )

        memory.add(user_input, response)

        return {
            "response": response,
            "action_taken": "coding",
        }

    except Exception as exc:
        logger.error("coding_error", error=str(exc), exc_info=True)
        return {
            "response": "Kodlama sürecinde bir hata oluştu Efendim.",
            "action_taken": "error",
        }

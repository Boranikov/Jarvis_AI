"""
Jarvis AI - Input Handler

Kullanıcı girdisi işleme ve engine routing.
"""

from enum import Enum
from typing import Any, Optional

from Brain.router import classify_intent
from Brain.intent_engine import process_command
from Brain.reasoning_engine import process_reasoning, format_reasoning_response
from Brain.coding_engine import process_coding_task
from Brain.plan_executor import execute_plan, format_execution_result
from Brain.memory import Memory
from Skills.skills_manager import perform_skill
from Core.display import print_debug
from Utils.math_validator import (
    validate_math_response,
    format_validation_result,
    llm_failed_to_solve,
    solve_directly,
)
from Config.config import PRESENCE_TRIGGERS, REQUIRED_PARAMS, MISSING_QUESTIONS, get_logger

logger = get_logger("core.handler")

# Skill çalıştırılmayan aksiyonlar
_NON_SKILL_ACTIONS: frozenset[str] = frozenset({"small_talk", "unknown", "missing_parameters", "multi_action"})

# Dosya/klasör işlemleri
_FILE_ACTIONS: frozenset[str] = frozenset({
    "create_file", "create_folder", "delete_file", "delete_folder", "write_to_file", "list_dir", 
    "read_file", "list_dir_recursive"
})


class OutputMode(Enum):
    """Çıktı modu: CLI print tabanlı, GUI return tabanlı."""
    CLI = "cli"
    GUI = "gui"




def _build_fast_model_params(result: dict[str, Any], user_input: str = "") -> dict[str, Any]:
    """Fast model sonucundan parametre dictionary'si oluştur."""
    parameters: Any = result.get("parameters", {})
    logger.debug("Fast model ham sonuç: action=%s, song_name=%s, path=%s, name=%s, parameters=%s",
                 result.get("action"), result.get("song_name"), result.get("path"), result.get("name"), parameters)
    if not isinstance(parameters, dict):
        parameters = {}

    # Üst seviye alanları parametrelere aktar
    for key in ("path", "name", "song_name", "query"):
        value: Optional[str] = result.get(key)
        if value:
            parameters[key] = value
        elif key in parameters and parameters[key]:
            # Model değeri parameters içine koymuşsa, üst seviyeye de yansıt
            result[key] = parameters[key]

    # Dosya/klasör işlemleri için varsayılan path
    action: str = result.get("action", "unknown")
    if action in _FILE_ACTIONS and not parameters.get("path"):
        parameters["path"] = "desktop"

    # play_music için fallback: LLM song_name döndüremediyse kullanıcı girdisinden çıkar
    if action == "play_music" and not parameters.get("song_name") and user_input:
        from Utils.helpers import clean_song_name
        fallback_name: str = clean_song_name(user_input)
        if fallback_name:
            parameters["song_name"] = fallback_name
            logger.debug("song_name fallback uygulandı: '%s'", fallback_name)

    logger.debug("Final parametreler: %s", parameters)
    return parameters


def process_input(
    user_input: str,
    memory: Memory,
    mode: OutputMode = OutputMode.CLI,
) -> Optional[str]:
    """Birleşik kullanıcı girdi işleyici."""
    # Presence Check
    normalized: str = user_input.lower()
    if any(trigger in normalized for trigger in PRESENCE_TRIGGERS):
        response = "Sizin için her zaman buradayım Efendim."
        if mode == OutputMode.CLI:
            print(f"Jarvis: {response}")
            return None
        return response

    if memory.has_pending():
        completed = memory.fill_pending(user_input)
        if completed:
            action: str = completed["action"]
            params: dict = completed["params"]
            logger.debug("Pending tamamlandı: %s — %s", action, params)
            skill_result = perform_skill(action, params)
            memory.clear_pending()
            reply: str = "İşleminiz tamamlandı Efendim." if skill_result else "İşlem başarısız oldu Efendim."
            if mode == OutputMode.CLI:
                print(f"Jarvis: {reply}")
                return None
            return reply
        # Hala eksik parametre var — sonraki soruyu bekle
        next_param: str = memory.pending_params[0] if memory.pending_params else "parametre"
        question: str = MISSING_QUESTIONS.get(
            memory.pending_action, {}
        ).get(next_param, f"{next_param} nedir?")
        if mode == OutputMode.CLI:
            print(f"Jarvis: {question}")
            return None
        return question

    route: str = classify_intent(user_input)

    logger.debug(
        "Pre-filter route: %s",
        {
            "coding": "coding (pre-filter)",
            "reasoning": "reasoning (pre-filter)",
        }.get(route, "intent engine"),
    )

    # Pre-filter: Coding veya Reasoning kesin tespitlerde direkt yönlendir
    if route == "coding":
        return _handle_coding(user_input, memory, mode)

    if route == "reasoning":
        return _handle_reasoning(user_input, {}, memory, mode)

    # Pre-filter belirsiz bıraktıysa — Intent Engine'e gönder (1 LLM çağrısı)
    return _handle_fast_model(user_input, memory, mode)


def _handle_reasoning(
    user_input: str,
    emotion_context: dict,
    memory: Memory,
    mode: OutputMode,
) -> Optional[str]:
    """
    Reasoning model ile karmaşık istekleri işle.
    emotion_context artık reasoning engine'in içinde üretiliyor;
    pre-filter'dan geliyorsa boş dict göndermek yeterli.
    """
    result: dict = process_reasoning(user_input, emotion_context if emotion_context else {})

    if not result.get("success"):
        fallback: str = result.get("response", "Bir sorun oluştu Efendim.")
        if mode == OutputMode.CLI:
            print(f"Jarvis: {fallback}")
            return None
        return fallback

    response: str = format_reasoning_response(result)

    # Matematik doğrulama (sadece input matematik içeriyorsa)
    _has_math: bool = any(c in user_input for c in "0123456789+-*/=")
    if _has_math and llm_failed_to_solve(response):
        logger.debug("LLM çözemedi, sympy/numpy devreye giriyor...")
        direct_result: dict = solve_directly(user_input)
        if direct_result["success"]:
            response = f"{direct_result['explanation']} Efendim."
            if mode == OutputMode.CLI:
                print(f"Jarvis: {response}")
                logger.debug(
                    "✓ %s ile hesaplandı: %s",
                    direct_result["method"],
                    direct_result["result"],
                )
            # Her iki modda da math sonrası plan yürütme devam eder
        else:
            if mode == OutputMode.CLI:
                print(f"Jarvis: {response}")
                if direct_result["explanation"]:
                    logger.debug("Math: %s", direct_result["explanation"])
    elif _has_math:
        if mode == OutputMode.CLI:
            print(f"Jarvis: {response}")
        validation: dict = validate_math_response(user_input, response)
        if validation["validated"]:
            validation_msg: str = format_validation_result(validation)
            if validation_msg:
                logger.debug("Math: %s", validation_msg)
    else:
        if mode == OutputMode.CLI:
            print(f"Jarvis: {response}")

    # Çalıştırılabilir adımlar (plan executor)
    executable_steps: Optional[list] = result.get("executable_steps")
    if executable_steps:
        logger.debug("%d adım yürütülecek...", len(executable_steps))
        execution_result: dict = execute_plan(executable_steps)
        execution_message: str = format_execution_result(execution_result)
        if execution_message:
            if mode == OutputMode.CLI:
                print(f"Jarvis: {execution_message}")
            response += f"\n\n{execution_message}"

    # Hafızaya ekle
    memory.add(user_input, response)

    return response if mode == OutputMode.GUI else None


def _handle_fast_model(
    user_input: str,
    memory: Memory,
    mode: OutputMode,
    emotion_context: Optional[dict] = None,
) -> Optional[str]:
    """
    Intent Engine ile komutu işle.
    Intent engine'in döndürdüğü `type` alanına göre yönlendir:
    - type="coding"    → coding engine
    - type="reasoning" → reasoning engine
    - type="skill"     → skill çalıştır
    - type="chat"      → reply donür
    """
    result: dict = process_command(user_input, memory.get_history())

    # Intent Engine'in type alanına göre yönlendir
    intent_type: str = result.get("type", "skill")

    if intent_type == "coding":
        logger.debug("type=coding → coding engine'e yönlendiriliyor")
        return _handle_coding(user_input, memory, mode)

    if intent_type == "reasoning":
        logger.debug("type=reasoning → reasoning engine'e yönlendiriliyor")
        return _handle_reasoning(user_input, {}, memory, mode)

    # type="skill" veya "chat" → normal akış
    action: str = result.get("action", "unknown")
    reply: str = result.get("reply", "Efendim?")
    parameters: dict = _build_fast_model_params(result, user_input)

    if mode == OutputMode.CLI:
        print(f"Jarvis: {reply}")
        print_debug(
            action,
            result.get("path"),
            result.get("name"),
            parameters,
            result.get("song_name"),
        )

    # Eksik parametre yönetimi
    if action == "missing_parameters":
        original_action: Optional[str] = result.get("original_action")
        missing: Optional[list] = parameters.get("missing") if isinstance(parameters.get("missing"), list) else result.get("parameters", {}).get("missing")
        if original_action and missing:
            original_params: dict = {}
            for key in ("path", "name", "song_name"):
                val = result.get(key)
                if val:
                    original_params[key] = val
            memory.set_pending(original_action, missing, original_params)
        return reply if mode == OutputMode.GUI else None

    required: tuple = REQUIRED_PARAMS.get(action, ())
    missing_params: list[str] = [p for p in required if not parameters.get(p)]
    if missing_params:
        logger.debug("Eksik parametreler (LLM kaçırdı): %s", missing_params)
        question: str = MISSING_QUESTIONS.get(action, {}).get(
            missing_params[0], f"{missing_params[0]} belirtilmedi Efendim."
        )
        memory.set_pending(action, missing_params, parameters)
        if mode == OutputMode.CLI:
            print(f"Jarvis: {question}")
            return None
        return question


    if action == "play_music" and not parameters.get("song_name"):
        if emotion_context and emotion_context.get("detected"):
            parameters["emotion"] = emotion_context["category"]

    # Multi-action: actions listesi varsa sırayla yürüt
    multi_actions: list = result.get("actions", [])
    if action == "multi_action" or (isinstance(multi_actions, list) and multi_actions):
        # write_to_file adımı içeriyorsa → coding engine'e yönlendir
        has_code_write: bool = any(
            isinstance(s, dict) and s.get("action") == "write_to_file" or s.get("action") == "read_file" or s.get("action") == "list_dir_recusive"
            for s in multi_actions
        )
        if has_code_write:
            logger.debug("write_to_file tespit edildi → coding engine'e yönlendiriliyor")
            return _handle_coding(user_input, memory, mode)

        # Kod yazmayan adımlar → plan executor ile çalıştır
        executable_steps: list[dict] = []
        for sub in multi_actions:
            if not isinstance(sub, dict) or not sub.get("action"):
                continue
            sub_params: dict = dict(sub.get("parameters") or {})
            for key in ("path", "name", "song_name", "query", "content"):
                val = sub.get(key)
                if val:
                    sub_params[key] = val
            # Dosya/klasör işlemleri için varsayılan path
            if sub["action"] in _FILE_ACTIONS and not sub_params.get("path"):
                sub_params["path"] = "desktop"
            executable_steps.append({"action": sub["action"], "params": sub_params})

        if executable_steps:
            logger.debug("%d adım yürütülecek (multi_action)...", len(executable_steps))
            execution_result: dict = execute_plan(executable_steps)
            execution_message: str = format_execution_result(execution_result)
            if execution_message and mode == OutputMode.CLI:
                print(f"Jarvis: {execution_message}")
            if mode == OutputMode.GUI:
                reply = reply + (f"\n{execution_message}" if execution_message else "")

        memory.add(user_input, reply)
        return reply if mode == OutputMode.GUI else None

    # Skill çalıştır (tekil aksiyon)
    if action not in _NON_SKILL_ACTIONS:
        skill_result = perform_skill(action, parameters)

        # get_current_track string döndürür — reply'ı güncelle
        if action == "get_current_track" and isinstance(skill_result, str):
            reply = f"Şu an çalan: {skill_result} Efendim."
            if mode == OutputMode.CLI:
                print(f"Jarvis: {reply}")

    # Hafızaya ekle
    memory.add(user_input, reply)

    return reply if mode == OutputMode.GUI else None


# Geriye uyumluluk
# Mevcut kodların bozulmaması için eski fonksiyon isimleri korunuyor.


def _handle_coding(
    user_input: str,
    memory: Memory,
    mode: OutputMode,
) -> Optional[str]:
    """
    Coding model (qwen2.5-coder:14b) ile kodlama isteklerini işle.

    Agentic döngü: Model dosya okuma/yazma/listeleme araçlarını
    kendi kendine çağırarak görevi tamamlar.

    Args:
        user_input: Kullanıcı girdisi
        memory: Hafıza nesnesi
        mode: Çıktı modu

    Returns:
        GUI modunda yanıt string'i, CLI modunda None
    """
    if mode == OutputMode.CLI:
        print("Jarvis: Kodlama motorunu başlatıyorum Efendim...")

    confirm_fn = None
    if mode == OutputMode.GUI:
        confirm_fn = lambda tool, name, preview: True

    result: dict = process_coding_task(
        user_input=user_input,
        confirm_fn=confirm_fn,
    )

    response: str = result.get("response", "İşlem tamamlandı Efendim.")
    actions: list = result.get("actions_taken", [])

    # Yapılan işlemleri logla
    if actions:
        logger.debug(
            "Coding: %d araç çağrısı yapıldı: %s",
            len(actions),
            ", ".join(a.get("tool", "?") for a in actions),
        )

    if mode == OutputMode.CLI:
        print(f"Jarvis: {response}")

    # Hafızaya ekle
    memory.add(user_input, response)

    return response if mode == OutputMode.GUI else None

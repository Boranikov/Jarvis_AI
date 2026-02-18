"""
Jarvis AI - Input Handler

Kullanıcı girdisi işleme ve model routing.
"""

from enum import Enum
from typing import Any, Optional

from Brain.router import classify_intent, detect_emotion
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
from config import PRESENCE_TRIGGERS, get_logger

logger = get_logger("core.handler")

# Skill çalıştırılmayan aksiyonlar
_NON_SKILL_ACTIONS: frozenset[str] = frozenset({"small_talk", "unknown", "missing_parameters"})

# Dosya/klasör işlemleri
_FILE_ACTIONS: frozenset[str] = frozenset({
    "create_file", "create_folder", "delete_file", "delete_folder",
})


class OutputMode(Enum):
    """Çıktı modu: CLI print tabanlı, GUI return tabanlı."""
    CLI = "cli"
    GUI = "gui"


def handle_presence_check(user_input: str) -> bool:
    """Sistem varlık kontrolü."""
    normalized: str = user_input.lower()
    if any(trigger in normalized for trigger in PRESENCE_TRIGGERS):
        print("Jarvis: Sizin için her zaman buradayım efendim.")
        return True
    return False


def _build_fast_model_params(result: dict[str, Any]) -> dict[str, Any]:
    """Fast model sonucundan parametre dictionary'si oluştur."""
    parameters: Any = result.get("parameters", {})
    if not isinstance(parameters, dict):
        parameters = {}

    # Alanları parametrelere aktar
    for key in ("path", "name", "song_name"):
        value: Optional[str] = result.get(key)
        if value:
            parameters[key] = value

    # Dosya/klasör işlemleri için varsayılan path
    action: str = result.get("action", "unknown")
    if action in _FILE_ACTIONS and not parameters.get("path"):
        parameters["path"] = "desktop"

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

    # Routing
    route: str = classify_intent(user_input)
    emotion_context: dict = detect_emotion(user_input)

    logger.debug(
        "Model: %s",
        {
            "coding": "qwen2.5-coder:14b (coding)",
            "reasoning": "qwen2.5:7b (reasoning)",
        }.get(route, "qwen2.5:3b (fast)"),
    )
    if emotion_context.get("detected"):
        logger.debug(
            "Duygu: %s — %s",
            emotion_context.get("category"),
            emotion_context.get("keywords"),
        )

    # Coding Model
    if route == "coding":
        return _handle_coding(user_input, memory, mode)

    # Reasoning Model
    if route == "reasoning":
        return _handle_reasoning(user_input, emotion_context, memory, mode)

    # Fast Model (Intent Engine)
    return _handle_fast_model(user_input, memory, mode)


def _handle_reasoning(
    user_input: str,
    emotion_context: dict,
    memory: Memory,
    mode: OutputMode,
) -> Optional[str]:
    """
    Reasoning model ile karmaşık istekleri işle.

    Args:
        user_input: Kullanıcı girdisi
        emotion_context: Duygu bilgisi
        memory: Hafıza nesnesi
        mode: Çıktı modu

    Returns:
        GUI modunda yanıt string'i, CLI modunda None
    """
    result: dict = process_reasoning(user_input, emotion_context)

    if not result.get("success"):
        fallback: str = result.get("response", "Bir sorun oluştu Efendim.")
        if mode == OutputMode.CLI:
            print(f"Jarvis: {fallback}")
            return None
        return fallback

    response: str = format_reasoning_response(result)

    # Matematik doğrulama
    if llm_failed_to_solve(response):
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
    else:
        if mode == OutputMode.CLI:
            print(f"Jarvis: {response}")
        # Matematik doğrulama (hibrit)
        validation: dict = validate_math_response(user_input, response)
        if validation["validated"]:
            validation_msg: str = format_validation_result(validation)
            if validation_msg:
                logger.debug("Math: %s", validation_msg)

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
) -> Optional[str]:
    """
    Fast model (Intent Engine) ile basit komutları işle.

    Args:
        user_input: Kullanıcı girdisi
        memory: Hafıza nesnesi
        mode: Çıktı modu

    Returns:
        GUI modunda yanıt string'i, CLI modunda None
    """
    result: dict = process_command(user_input, memory.get_history())

    action: str = result.get("action", "unknown")
    reply: str = result.get("reply", "Efendim?")
    parameters: dict = _build_fast_model_params(result)

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

    # Skill çalıştır
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

    # GUI modunda onay callback'i
    confirm_fn = None
    if mode == OutputMode.GUI:
        # GUI için şimdilik otomatik onay (ileride GUI dialog eklenebilir)
        confirm_fn = None  # CLI varsayılanı kullanır

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


def process_user_input(user_input: str, memory: Memory) -> None:
    """Geriye uyumluluk: CLI modu için process_input wrapper."""
    process_input(user_input, memory, OutputMode.CLI)


def process_user_input_for_gui(user_input: str, memory: Memory) -> str:
    """Geriye uyumluluk: GUI modu için process_input wrapper."""
    return process_input(user_input, memory, OutputMode.GUI) or ""

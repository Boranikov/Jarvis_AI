"""
Jarvis AI - Skills Manager

Tüm skill'leri tek noktadan yöneten adapter katmanı.

Mimari:
- SKILL_MAP: action → fonksiyon eşleştirmesi
- SKILL_SCHEMA_MAP: action → Pydantic şema sınıfı eşleştirmesi
- perform_skill(): gelen ham dict'i uygun Pydantic modeline dönüştürüp fonksiyonu çağırır.
  Bu sayede kodun geri kalanı (handler, coding_engine, plan_executor) hâlâ dict gönderebilir.
"""

from typing import Callable, Optional, Type

from pydantic import BaseModel, ValidationError

from Skills.file_skills import (
    FileBaseParams, WriteFileParams, ListDirParams,
    create_file, create_folder, delete_file, delete_folder,
    list_dir_recursive, read_file, write_to_file,
)
from Skills.music_skills import (
    PlayMusicParams, NoParams,
    play_music, pause_music, resume_music, get_current_track, next_track,
)
from Skills.web_skills import WebSearchParams, web_search
from Config.config import get_logger

logger = get_logger("skills.manager")

# -------------------------------------------------------
# Aksiyon → Fonksiyon eşleştirmesi
# -------------------------------------------------------
SKILL_MAP: dict[str, Callable] = {
    "create_file":        create_file,
    "create_folder":      create_folder,
    "delete_file":        delete_file,
    "delete_folder":      delete_folder,
    "read_file":          read_file,
    "write_to_file":      write_to_file,
    "list_dir_recursive": list_dir_recursive,
    "play_music":         play_music,
    "pause_music":        pause_music,
    "resume_music":       resume_music,
    "get_current_track":  get_current_track,
    "next_track":         next_track,
    "web_search":         web_search,
}

# -------------------------------------------------------
# Aksiyon → Pydantic Şema eşleştirmesi
# None = parametre gerektirmiyor, NoParams kullan
# -------------------------------------------------------
SKILL_SCHEMA_MAP: dict[str, Optional[Type[BaseModel]]] = {
    "create_file":        FileBaseParams,
    "create_folder":      FileBaseParams,
    "delete_file":        FileBaseParams,
    "delete_folder":      FileBaseParams,
    "read_file":          FileBaseParams,
    "write_to_file":      WriteFileParams,
    "list_dir_recursive": ListDirParams,
    "play_music":         PlayMusicParams,
    "pause_music":        NoParams,
    "resume_music":       NoParams,
    "get_current_track":  NoParams,
    "next_track":         NoParams,
    "web_search":         WebSearchParams,
}


def perform_skill(action: str, params: dict) -> bool | str | None:
    """
    Belirtilen aksiyonu gerçekleştir.

    Ham dict parametresini, aksiyona karşılık gelen Pydantic modeline dönüştürür
    ve ilgili skill fonksiyonunu çağırır. Dönüşüm başarısız olursa hata loglanır ve
    False döner. Bu sayede çağıran kod (handler, coding_engine, plan_executor) hiç
    değişmeden dict göndermeye devam edebilir.

    Args:
        action: Gerçekleştirilecek aksiyon adı (SKILL_MAP'teki bir key).
        params: Aksiyon parametrelerini içeren ham dict.

    Returns:
        Skill sonucu (True/False veya bazı skill'ler için str).
    """
    if not isinstance(params, dict):
        logger.error("Parametreler hatalı format: %s", type(params).__name__)
        return False

    skill_func = SKILL_MAP.get(action)
    if not skill_func:
        logger.warning("Bilinmeyen aksiyon: %s", action)
        return False

    schema_class = SKILL_SCHEMA_MAP.get(action)

    # Şema sınıfı tanımlı → dict'i Pydantic'e dönüştür
    if schema_class is not None:
        try:
            typed_params = schema_class(**params)
        except ValidationError as exc:
            logger.error("Parametre doğrulama hatası [%s]: %s", action, exc)
            return False
        return skill_func(typed_params)

    # Şema tanımlı değil → doğrudan dict ile çağır (legacy fallback)
    return skill_func(params)


def get_tool_schemas() -> list[dict]:
    """
    Tüm skill'lerin JSON şemalarını LLM için hazır formatta döndürür.
    Native Function Calling (Ollama / OpenAI tool format) için kullanılır.

    Returns:
        [{"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}, ...]
    """
    schemas: list[dict] = []
    for action, schema_class in SKILL_SCHEMA_MAP.items():
        if schema_class is None:
            continue
        json_schema = schema_class.model_json_schema()
        schemas.append({
            "type": "function",
            "function": {
                "name": action,
                "description": json_schema.get("description", action),
                "parameters": json_schema,
            },
        })
    return schemas

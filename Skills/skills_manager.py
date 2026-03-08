"""
Jarvis AI - Skills Manager

Tüm skill'leri tek noktadan yöneten adapter katmanı.

Mimari:
- SKILL_MAP: action → fonksiyon eşleştirmesi
- perform_skill(): gelen ham dict'i alıp kwargs olarak ilgili fonksiyona geçirir.
- get_tool_schemas(): SchemaGenerator kullanarak fonksiyonları LLM tool'larına dönüştürür.
"""

from typing import Callable, Any, Optional

from Skills.file_skills import (
    create_file, create_folder, delete_file, delete_folder,
    list_dir_recursive, read_file, write_to_file,
)
from Skills.music_skills import (
    play_music, pause_music, resume_music, get_current_track, next_track,
)
from Skills.web_skills import web_search
from Core.schema_generator import SchemaGenerator
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

def perform_skill(action: str, params: dict) -> Any:
    """
    Belirtilen aksiyonu gerçekleştirir.
    
    Args:
        action: Gerçekleştirilecek aksiyon adı (SKILL_MAP'teki bir key).
        params: Aksiyon parametrelerini içeren sözlük (kwargs olarak fonksiyona geçirilir).
        
    Returns:
        Skill sonucu.
    """
    if not isinstance(params, dict):
        logger.error("Parametreler hatalı format: %s", type(params).__name__)
        return False

    skill_func = SKILL_MAP.get(action)
    if not skill_func:
        logger.warning("Bilinmeyen aksiyon: %s", action)
        return False

    try:
        # Pydantic olmadan doğrudan Python kwargs olarak geçiriyoruz
        return skill_func(**params)
    except TypeError as exc:
        logger.error("Parametre eşleşme hatası [%s]: %s", action, exc)
        return False
    except Exception as exc:
        logger.error("Skill çalıştırma hatası [%s]: %s", action, exc)
        return False


def get_tool_schemas() -> list[dict]:
    """
    Tüm skill'lerin JSON şemalarını LLM için hazır formatta döndürür.
    SchemaGenerator sınıfını kullanarak dinamik olarak Python docstring'lerinden okur.

    Returns:
        [{"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}, ...]
    """
    schemas: list[dict] = []
    for action, func in SKILL_MAP.items():
        try:
            schema = SchemaGenerator.generate_tool_schema(func)
            schemas.append(schema)
        except Exception as exc:
            logger.error("Şema oluşturma hatası [%s]: %s", action, exc)
    return schemas

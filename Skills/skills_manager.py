"""
Jarvis AI - Skills Manager

Skill yönlendirici — aksiyonları ilgili skill'lere yönlendirir.

Optimizasyonlar:
- Type hints
- Logging
"""

from typing import Callable

from Skills.file_skills import create_file, create_folder, delete_file, delete_folder, list_dir_recursive, read_file, write_to_file
from Skills.music_skills import play_music, pause_music, resume_music, get_current_track, next_track
from Skills.web_skills import web_search
from config import get_logger

logger = get_logger("skills.manager")

# Aksiyon → Fonksiyon eşleştirmesi
SKILL_MAP: dict[str, Callable[[dict], bool]] = {
    "create_file": create_file,
    "create_folder": create_folder,
    "delete_file": delete_file,
    "delete_folder": delete_folder,
    "play_music": play_music,
    "web_search": web_search,
    "pause_music": pause_music,
    "resume_music": resume_music,
    "get_current_track": get_current_track,
    "next_track": next_track,
    "list_dir_recursive": list_dir_recursive,
    "read_file": read_file,
    "write_to_file": write_to_file,
}


def perform_skill(action: str, params: dict) -> bool | str | None:
    """
    Belirtilen aksiyonu gerçekleştir.

    Args:
        action: Gerçekleştirilecek aksiyon
        params: Aksiyon parametreleri

    Returns:
        Başarılı ise True
    """
    if not isinstance(params, dict):
        logger.error("Parametreler hatalı format: %s", type(params).__name__)
        return False

    skill_func: Callable | None = SKILL_MAP.get(action)

    if skill_func:
        return skill_func(params)

    logger.warning("Bilinmeyen aksiyon: %s", action)
    return False

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
    play_specific_music, play_emotion_music, pause_music, resume_music, get_current_track, next_track,
)
from Skills.terminal_skills import run_terminal_command
from Skills.webhook_skills import trigger_n8n_workflow
from Skills.web_skills import web_search
from Core.schema_generator import SchemaGenerator
from MCP.tool_registry import get_all_tool_schemas, call_mcp_tool_async
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
    "play_specific_music": play_specific_music,
    "play_emotion_music": play_emotion_music,
    "pause_music":        pause_music,
    "resume_music":       resume_music,
    "get_current_track":  get_current_track,
    "next_track":         next_track,
    "web_search":         web_search,
    "run_terminal_command": run_terminal_command,
    "trigger_n8n_workflow": trigger_n8n_workflow,
}

import asyncio

async def perform_skill(action: str, params: dict) -> Any:
    """
    Belirtilen aksiyonu asenkron olarak gerçekleştirir.
    
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
        # MCP'de böyle bir araç var mı diye kontrol et ve çalıştır (Asenkron)
        logger.debug(f"Bilinmeyen lokal aksiyon '{action}'. MCP üzerinde deneniyor...")
        try:
            return await call_mcp_tool_async(action, params)
        except Exception as e:
            logger.warning(f"Bilinmeyen aksiyon (MCP dahil): {action} -> {e}")
            return False

    try:
        # Eğer fonksiyon async ise await ile çalıştır, değilse blocking IO'yu önlemek için to_thread kullan
        if asyncio.iscoroutinefunction(skill_func):
            return await skill_func(**params)
        else:
            return await asyncio.to_thread(skill_func, **params)
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
            
    # Dinamik MCP Tool'larını çekip listeye ekle
    try:
        mcp_schemas = get_all_tool_schemas()
        schemas.extend(mcp_schemas)
    except Exception as exc:
        logger.error(f"MCP Tool şemaları çekilemedi: {exc}")

    return schemas

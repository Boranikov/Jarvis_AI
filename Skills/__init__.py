"""
Jarvis AI - Skills Module

Tüm skill'ler ve Pydantic şemalarını dışa açar.
"""

from Skills.skills_manager import perform_skill, get_tool_schemas, SKILL_MAP, SKILL_SCHEMA_MAP
from Skills.file_skills import (
    FileBaseParams, WriteFileParams, ListDirParams,
    create_file, create_folder, delete_file, delete_folder,
    read_file, write_to_file, list_dir_recursive,
)
from Skills.music_skills import (
    PlayMusicParams, NoParams,
    play_music, pause_music, resume_music, get_current_track, next_track,
)
from Skills.web_skills import WebSearchParams, web_search

__all__ = [
    # Manager
    "perform_skill",
    "get_tool_schemas",
    "SKILL_MAP",
    "SKILL_SCHEMA_MAP",
    # File Skills
    "FileBaseParams", "WriteFileParams", "ListDirParams",
    "create_file", "create_folder", "delete_file", "delete_folder",
    "read_file", "write_to_file", "list_dir_recursive",
    # Music Skills
    "PlayMusicParams", "NoParams",
    "play_music", "pause_music", "resume_music", "get_current_track", "next_track",
    # Web Skills
    "WebSearchParams", "web_search",
]

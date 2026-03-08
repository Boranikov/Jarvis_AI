"""
Jarvis AI - Skills Module

Tüm skill'leri dışa açar.
"""

from Skills.skills_manager import perform_skill, get_tool_schemas, SKILL_MAP
from Skills.file_skills import (
    create_file, create_folder, delete_file, delete_folder,
    read_file, write_to_file, list_dir_recursive,
)
from Skills.music_skills import (
    play_music, pause_music, resume_music, get_current_track, next_track,
)
from Skills.web_skills import web_search

__all__ = [
    # Manager
    "perform_skill",
    "get_tool_schemas",
    "SKILL_MAP",
    # File Skills
    "create_file", "create_folder", "delete_file", "delete_folder",
    "read_file", "write_to_file", "list_dir_recursive",
    # Music Skills
    "play_music", "pause_music", "resume_music", "get_current_track", "next_track",
    # Web Skills
    "web_search",
]

"""
Jarvis AI - Display Functions

Kullanıcı arayüzü ve çıktı fonksiyonları.
"""

from typing import Any, Optional

from config import get_logger

logger = get_logger("core.display")


def print_header() -> None:
    """CLI başlangıç banner'ını yazdır."""
    print("=" * 50)
    print("              JARVIS AI ASSISTANT")
    print("=" * 50)
    print("\nKullanıcı ile konuşmaya başlamak için yazın.")
    print("Çıkmak için 'çık' veya 'exit' yazın.\n")


def print_debug(
    action: str,
    path: Optional[str],
    name: Optional[str],
    parameters: Any,
    song_name: Optional[str] = None,
) -> None:
    """Debug bilgilerini logla."""
    params_str: str = str(parameters) if isinstance(parameters, dict) and parameters else "{}"
    logger.debug("Action=%s, Path=%s, Name=%s, Params=%s", action, path, name, params_str)

    if action == "play_music" and song_name:
        logger.debug("Song Name=%s", song_name)

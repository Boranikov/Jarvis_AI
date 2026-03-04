"""
Jarvis AI - Helper Utilities

Genel yardımcı fonksiyonlar.
"""

from typing import Any, Optional

from Config.config import get_logger

logger = get_logger("utils.helpers")

_MUSIC_COMMAND_WORDS: frozenset[str] = frozenset({
    "çal", "oynat", "aç", "dinle", "başlat",
    "spotify", "spotifydan", "spotify'dan", "müzik",
})


def debug_print(message: str, data: Optional[dict[str, Any]] = None) -> None:
    """Debug mesajını logla."""
    logger.debug(message)
    if data:
        for key, value in data.items():
            logger.debug("  - %s: %s", key, value)


def clean_song_name(song_name: str) -> str:
    """Şarkı adından komut kelimelerini temizle."""
    if not song_name:
        return ""

    words: list[str] = song_name.lower().split()
    cleaned: list[str] = [w for w in words if w not in _MUSIC_COMMAND_WORDS]
    return " ".join(cleaned).strip()

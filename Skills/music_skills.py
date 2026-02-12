"""
Jarvis AI - Music Skills

Müzik çalma işlemleri.
"""

import urllib.parse
import webbrowser
from typing import Optional

from Utils.helpers import clean_song_name
from config import get_logger

logger = get_logger("skills.music")


def play_music(params: dict) -> bool:
    """
    Spotify'da müzik ara ve çal.

    Args:
        params: song_name içeren dictionary

    Returns:
        Başarılı ise True
    """
    song_name: Optional[str] = params.get("song_name")

    if not song_name:
        logger.error("Çalacak müzik belirtilmedi")
        return False

    cleaned: str = clean_song_name(song_name)

    if not cleaned:
        logger.error("Temizleme sonrası şarkı adı boş kaldı")
        return False

    try:
        encoded: str = urllib.parse.quote(cleaned)
        webbrowser.open(f"spotify:search:{encoded}")
        logger.info("Spotify'da '%s' aranıyor...", cleaned)
        return True
    except OSError as exc:
        logger.error("Spotify açma başarısız: %s", exc)
        return False

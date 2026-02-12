"""
Jarvis AI - Web Skills

Web araması işlemleri.
"""

import urllib.parse
import webbrowser
from typing import Optional

from config import get_logger

logger = get_logger("skills.web")


def web_search(params: dict) -> bool:
    """
    Google'da arama yap.

    Args:
        params: name içeren dictionary

    Returns:
        Başarılı ise True
    """
    query: Optional[str] = params.get("name")

    if not query:
        logger.error("Arama terimi belirtilmedi")
        return False

    try:
        encoded: str = urllib.parse.quote(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        logger.info("Google'da '%s' aranıyor...", query)
        return True
    except OSError as exc:
        logger.error("Google açma başarısız: %s", exc)
        return False

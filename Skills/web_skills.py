"""
Jarvis AI - Web Skills

Web araması işlemleri. Tüm parametre doğrulaması yerel argümanlarla yapılır.
"""

import urllib.parse
import webbrowser

from Config.config import get_logger

logger = get_logger("skills.web")


# ==========================================
# YETENEK FONKSİYONLARI (SKILLS)
# ==========================================

def web_search(name: str) -> bool:
    """Google'da verilen terimi arar ve yeni sekmede açar."""
    try:
        encoded = urllib.parse.quote(name)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        logger.info("Google'da '%s' aranıyor", name)
        return True
    except OSError as exc:
        logger.error("Google açma başarısız: %s", exc)
        return False

"""
Jarvis AI - Web Skills

Web araması işlemleri. Tüm parametre doğrulaması Pydantic modelleri ile yapılır.
"""

import urllib.parse
import webbrowser

from pydantic import BaseModel, Field

from Config.config import get_logger

logger = get_logger("skills.web")


# ==========================================
# PYDANTIC MODELLERİ
# ==========================================

class WebSearchParams(BaseModel):
    """Google araması için şema."""
    name: str = Field(
        ...,
        description="Google'da aranacak terim veya soru (örnek: 'Python nedir', 'hava durumu İstanbul').",
    )


# ==========================================
# YETENEK FONKSİYONLARI (SKILLS)
# ==========================================

def web_search(params: WebSearchParams) -> bool:
    """Google'da arama yap ve tarayıcıda aç."""
    try:
        encoded = urllib.parse.quote(params.name)
        webbrowser.open(f"https://www.google.com/search?q={encoded}")
        logger.info("Google'da '%s' aranıyor", params.name)
        return True
    except OSError as exc:
        logger.error("Google açma başarısız: %s", exc)
        return False

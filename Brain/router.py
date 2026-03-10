"""
Jarvis AI - Semantic Router

Kullanıcı girdisini analiz edip hangi modelin veya yeteneğin kullanılacağına
anlamsal (semantic) vektörler üzerinden karar verir.
"""

from typing import Optional

from semantic_router import Route, RouteLayer
from semantic_router.encoders import OllamaEncoder
from Config.settings import get_settings
from Config.logging_config import get_logger

logger = get_logger("brain.router")

_route_layer = None

def _get_route_layer() -> RouteLayer:
    """Lazy initializing for route layer."""
    global _route_layer
    if _route_layer is None:
        settings = get_settings()
        
        encoder = OllamaEncoder(
            model=settings.embedding_model,
            base_url=settings.ollama_base_url
        )
        
        # Kodlama (Coding) Rotası
        coding_route = Route(
            name="coding",
            utterances=[
                "hesap makinesi kodu yaz",
                "python scripti oluştur",
                "bug'ı bul",
                "fonksiyonu refactor et",
                "şunu optimize et",
                "hata nerede",
                "dosyasına şu kodu ekle",
                "uygulama yaz",
            ],
            score_threshold=0.6,
        )
        
        # Mantık (Reasoning) Rotası
        reasoning_route = Route(
            name="reasoning",
            utterances=[
                "mimari nasıl çalışır",
                "bunun farkı nedir",
                "neden böyle bir hata alıyorum",
                "bunu bana açıkla",
                "nasıl yapabilirim",
                "hangi veritabanı daha iyi",
                "plan oluştur",
                "stresliyim yardım et",
                "canım sıkkın",
                "moralim bozuk",
            ],
            score_threshold=0.6,
        )

        # Hızlı (Fast Action/Chat) Rotası
        fast_route = Route(
            name="fast",
            utterances=[
                "merhaba",
                "nasılsın",
                "orda mısın",
                "klasör oluştur",
                "dosya sil",
                "müzik çal",
                "şarkıyı durdur",
                "internette ara",
                "saat kaç",
            ],
            score_threshold=0.6,
        )

        _route_layer = RouteLayer(encoder=encoder, routes=[coding_route, reasoning_route, fast_route])
        logger.info("Semantic Router başarıyla başlatıldı.")
        
    return _route_layer


def classify_intent(user_input: str) -> str:
    """Kullanıcı girdisini analiz edip 'coding', 'reasoning' veya 'fast' döndürür."""
    if not user_input.strip():
        return "fast"
        
    try:
        route_layer = _get_route_layer()
        match = route_layer(user_input)
        
        if match.name == "coding":
            return "coding"
        if match.name == "reasoning":
            return "reasoning"
            
        return "fast"
    except Exception as exc:
        logger.error(f"Semantic Router Hatası: {exc}")
        return "fast" # Fallback


# Duygu analizi için basit LLM bazlı veya fast keyword fallback
def detect_emotion(user_input: str) -> dict[str, object]:
    """
    (Opsiyonel) Emotion Detection logic.
    Şu an basit tutuldu, ileride LLM tabanlı Extraction'a geçirilecek.
    """
    text = user_input.lower()
    if any(w in text for w in ["sinirli", "kızgın", "öfkeli", "sıkıldım", "üzgün", "mutsuz", "yorgun"]):
        return {"detected": True, "category": "negative", "keywords": []}
    if any(w in text for w in ["mutlu", "heyecanlı"]):
        return {"detected": True, "category": "positive", "keywords": []}
    return {"detected": False, "category": None, "keywords": []}

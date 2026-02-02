"""
Jarvis AI - Model Router
Kullanıcı girdisini analiz edip hangi modelin kullanılacağına karar verir.
"""

import re

# Reasoning model (qwen2.5:7b) gerektiren tetikleyiciler
REASONING_TRIGGERS = [
    # Soru kelimeleri
    "nedir", "nelerdir", "nasıl", "neden", "niçin", "ne zaman",
    "kim", "hangi", "kaç", "ne kadar",
    # Açıklama istekleri
    "açıkla", "anlat", "öğret", "tarif et", "detay",
    # Planlama kelimeleri
    "plan", "planla", "adım", "adımlar", "strateji",
    "analiz", "analiz et", "düşün", "değerlendir",
    # Karmaşık istekler
    "karşılaştır", "fark", "avantaj", "dezavantaj",
    "öneri", "öner", "tavsiye", "yardım et"
]

# Duygu durumu kelimeleri (reasoning model ile işlenecek)
EMOTION_KEYWORDS = [
    # Olumsuz duygular
    "sinirli", "kızgın", "öfkeli", "sıkıldım", "sıkılıyorum",
    "üzgün", "mutsuz", "yorgun", "stresli", "bunaldım",
    "canım sıkkın", "moralim bozuk", "hayal kırıklığı",
    # Olumlu duygular
    "mutlu", "heyecanlı", "meraklı", "ilgili",
    # Belirsizlik
    "kafam karışık", "emin değilim", "anlamadım", "kararsız"
]

# Hızlı model (qwen2.5:3b) için doğrudan aksiyon kelimeleri
FAST_ACTION_KEYWORDS = [
    # Dosya işlemleri
    "oluştur", "aç", "sil", "kaldır", "klasör", "dosya",
    # Müzik
    "çal", "müzik", "şarkı", "spotify",
    # Web
    "ara", "araştır", "google", "internette",
    # Small talk (selamlama)
    "merhaba", "selam", "günaydın", "iyi akşamlar",
    "nasılsın", "naber", "ne haber"
]


def classify_intent(user_input: str) -> str:
    """
    Kullanıcı girdisini analiz edip hangi modelin kullanılacağına karar verir.
    
    Args:
        user_input: Kullanıcı girdisi
        
    Returns:
        "reasoning" veya "fast"
    """
    text = user_input.lower().strip()
    
    # Soru işareti kontrolü - genellikle reasoning gerektirir
    if "?" in text:
        # Ama basit sorular hızlı modelle işlenebilir
        if any(kw in text for kw in ["mısın", "misin", "orada mısın", "orda mısın"]):
            return "fast"
        return "reasoning"
    
    # Duygu durumu tespit edilirse reasoning
    for emotion in EMOTION_KEYWORDS:
        if emotion in text:
            return "reasoning"
    
    # Reasoning trigger kelimeleri kontrol et
    for trigger in REASONING_TRIGGERS:
        if trigger in text:
            return "reasoning"
    
    # Hızlı aksiyon kelimeleri varsa fast
    for action in FAST_ACTION_KEYWORDS:
        if action in text:
            return "fast"
    
    # Varsayılan olarak fast model kullan
    return "fast"


def detect_emotion(user_input: str) -> dict:
    """
    Kullanıcı girdisinden duygu durumu tespit et.
    
    Args:
        user_input: Kullanıcı girdisi
        
    Returns:
        Duygu bilgisi dictionary: {"detected": bool, "emotion": str, "keywords": list}
    """
    text = user_input.lower()
    detected_emotions = []
    
    for emotion in EMOTION_KEYWORDS:
        if emotion in text:
            detected_emotions.append(emotion)
    
    if detected_emotions:
        # Ana duygu kategorisini belirle
        negative = ["sinirli", "kızgın", "öfkeli", "sıkıldım", "sıkılıyorum",
                   "üzgün", "mutsuz", "yorgun", "stresli", "bunaldım",
                   "canım sıkkın", "moralim bozuk", "hayal kırıklığı"]
        positive = ["mutlu", "heyecanlı", "meraklı", "ilgili"]
        
        if any(e in negative for e in detected_emotions):
            category = "negative"
        elif any(e in positive for e in detected_emotions):
            category = "positive"
        else:
            category = "neutral"
        
        return {
            "detected": True,
            "category": category,
            "keywords": detected_emotions
        }
    
    return {"detected": False, "category": None, "keywords": []}

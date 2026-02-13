"""
Jarvis AI - Model Router

Kullanıcı girdisini analiz edip hangi modelin kullanılacağına karar verir.
"""

import re
from typing import Optional

from config import get_logger

logger = get_logger("brain.router")

# Keyword Sets

# Tek kelimelik reasoning trigger'ları (token match)
_REASONING_WORD_TRIGGERS: frozenset[str] = frozenset({
    "nedir", "nelerdir", "nasıl", "neden", "niçin",
    "kim", "hangi", "kaç",
    "açıkla", "anlat", "öğret", "detay",
    "plan", "planla", "adım", "adımlar", "strateji",
    "analiz", "düşün", "değerlendir",
    "karşılaştır", "fark", "avantaj", "dezavantaj",
    "öneri", "öner", "tavsiye",
})

# Çok kelimelik reasoning trigger'ları (substring match zorunlu)
_REASONING_PHRASE_TRIGGERS: tuple[str, ...] = (
    "ne zaman", "ne kadar", "tarif et", "analiz et", "yardım et",
)

# Hızlı aksiyon kelimeleri (token match)
_FAST_ACTION_KEYWORDS: frozenset[str] = frozenset({
    "oluştur", "aç", "sil", "kaldır", "klasör", "dosya",
    "çal", "müzik", "şarkı", "spotify",
    "ara", "araştır", "google", "internette",
    "merhaba", "selam", "günaydın", "nasılsın", "naber",
    "hava","hava durumu"
})

# Çok kelimelik hızlı aksiyon trigger'ları
_FAST_PHRASE_TRIGGERS: tuple[str, ...] = (
    "iyi akşamlar", "ne haber",
)

# Matematik kelimeleri (token match)
_MATH_WORD_KEYWORDS: frozenset[str] = frozenset({
    "kare", "karekök", "üslü", "üzeri", "faktöriyel",
    "hesapla", "çöz", "denklem", "eşitlik",
    "toplam", "çarp", "böl", "çıkar", "ekle",
})

# Matematik operatörleri (karakter match)
_MATH_OPERATORS: frozenset[str] = frozenset({
    "+", "-", "*", "/", "^", "!", "=",
})

# Dosya aksiyon kelimeleri (çoklu işlem tespiti için)
_FILE_ACTION_KEYWORDS: frozenset[str] = frozenset({
    "oluştur", "aç", "sil", "kaldır",
})

# Sıralı işlem ifadeleri
_SEQUENTIAL_KEYWORDS: frozenset[str] = frozenset({
    "içine", "sonra", "ardından", "içinde",
})

_SEQUENTIAL_PHRASE: tuple[str, ...] = ("daha sonra",)

# Basit soru kelimeleri (fast model yeterli)
_SIMPLE_QUESTION_KEYWORDS: frozenset[str] = frozenset({
    "mısın", "misin",
})

_SIMPLE_QUESTION_PHRASES: tuple[str, ...] = (
    "orada mısın", "orda mısın",
)

_MATH_PATTERN: re.Pattern = re.compile(r"\d+\s*[\+\-\*\/\^]\s*\d+")

# Duygu Keyword'leri
_EMOTION_KEYWORD_MAP: dict[str, str] = {
    # Olumsuz
    "sinirli": "negative",
    "kızgın": "negative",
    "öfkeli": "negative",
    "sıkıldım": "negative",
    "sıkılıyorum": "negative",
    "üzgün": "negative",
    "mutsuz": "negative",
    "yorgun": "negative",
    "stresli": "negative",
    "bunaldım": "negative",
    # Olumlu
    "mutlu": "positive",
    "heyecanlı": "positive",
    "meraklı": "positive",
    "ilgili": "positive",
    # Belirsizlik
    "kararsız": "neutral",
}

# Çok kelimelik duygu ifadeleri
_EMOTION_PHRASE_MAP: dict[str, str] = {
    "canım sıkkın": "negative",
    "moralim bozuk": "negative",
    "hayal kırıklığı": "negative",
    "kafam karışık": "neutral",
    "emin değilim": "neutral",
    "anlamadım": "neutral",
}

# Hızlı token-bazlı duygu seti (classify_intent'de kullanılır)
_EMOTION_ALL_WORDS: frozenset[str] = frozenset(_EMOTION_KEYWORD_MAP.keys())


def classify_intent(user_input: str) -> str:
    """Kullanıcı girdisini analiz edip 'reasoning' veya 'fast' döndürür."""
    text: str = user_input.lower().strip()
    tokens: list[str] = text.split()
    token_set: frozenset[str] = frozenset(tokens)

    # 1) Soru işareti → genelde reasoning
    if "?" in text:
        # Basit sorular hızlı modelle yeterli
        if token_set & _SIMPLE_QUESTION_KEYWORDS or any(p in text for p in _SIMPLE_QUESTION_PHRASES):
            return "fast"
        return "reasoning"

    # 2) Duygu durumu
    if token_set & _EMOTION_ALL_WORDS:
        return "reasoning"
    # Çok kelimelik duygu ifadesi kontrolü
    if any(phrase in text for phrase in _EMOTION_PHRASE_MAP):
        return "reasoning"

    # 3) Reasoning trigger'ları (token match)
    if token_set & _REASONING_WORD_TRIGGERS:
        return "reasoning"
    if any(phrase in text for phrase in _REASONING_PHRASE_TRIGGERS):
        return "reasoning"

    # 4) Çoklu işlem tespiti
    action_count: int = len(token_set & _FILE_ACTION_KEYWORDS)
    if action_count >= 1:
        # "ve" bağlacı ile çoklu işlem
        if " ve " in text:
            return "reasoning"
        # Sıralı işlem ifadeleri
        if token_set & _SEQUENTIAL_KEYWORDS or any(p in text for p in _SEQUENTIAL_PHRASE):
            return "reasoning"

    # 5) Matematik tespiti
    if token_set & _MATH_WORD_KEYWORDS:
        return "reasoning"
    # Operatör karakter kontrolü
    if any(op in text for op in _MATH_OPERATORS):
        return "reasoning"
    # Sayı + operatör + sayı paterni (derlenmiş regex)
    if _MATH_PATTERN.search(text):
        return "reasoning"

    # 6) Hızlı aksiyon kelimeleri
    if token_set & _FAST_ACTION_KEYWORDS:
        return "fast"
    if any(phrase in text for phrase in _FAST_PHRASE_TRIGGERS):
        return "fast"

    # 7) Varsayılan
    return "fast"


def detect_emotion(user_input: str) -> dict[str, object]:
    """Kullanıcı girdisinden duygu durumu tespit et."""
    text: str = user_input.lower()
    tokens: list[str] = text.split()
    detected_keywords: list[str] = []
    categories_found: set[str] = set()

    # Token-bazlı kontrol (O(T), T = token sayısı)
    for token in tokens:
        category: Optional[str] = _EMOTION_KEYWORD_MAP.get(token)
        if category:
            detected_keywords.append(token)
            categories_found.add(category)

    # Çok kelimelik ifade kontrolü
    for phrase, category in _EMOTION_PHRASE_MAP.items():
        if phrase in text:
            detected_keywords.append(phrase)
            categories_found.add(category)

    if detected_keywords:
        # Öncelik: negative > positive > neutral
        if "negative" in categories_found:
            final_category = "negative"
        elif "positive" in categories_found:
            final_category = "positive"
        else:
            final_category = "neutral"

        return {
            "detected": True,
            "category": final_category,
            "keywords": detected_keywords,
        }

    return {"detected": False, "category": None, "keywords": []}

"""
Jarvis AI - Reasoning Engine

qwen2.5:7b modeli ile düşünme, planlama ve duygu analizi.
"""

import json
import re
from typing import Any, Optional

import ollama

from config import REASONING_MODEL, REASONING_TEMPERATURE, get_logger

logger = get_logger("brain.reasoning")

REASONING_SYSTEM_PROMPT: str = """
Sen Jarvis'in düşünme katmanısın. Kullanıcının karmaşık sorularını, duygusal durumunu ve planlama ihtiyaçlarını analiz edersin.

Kurallar:
- Her zaman Türkçe cevap ver.
- Kullanıcıya "Efendim" diye hitap et.
- Yanıtları JSON formatında ver.
- İnternete yönlendirme yapma, kendi bilginle cevap ver.
- Empati göster ve yardımcı ol.

Görevlerin:
1. BİLGİ SORULARI: "X nedir?", "Y nasıl çalışır?" gibi soruları kendi bilginle cevapla.
2. DUYGU ANALİZİ: Kullanıcının duygusal durumunu tespit et ve ona göre yanıt ver.
3. PLANLAMA: Karmaşık istekleri adımlara böl, plan oluştur VE çalıştırılabilir adımları üret.
4. TAVSİYE: Önerilerde bulun, yardımcı ol.

ÇALIŞTIRILABİLİR ADIMLAR (executable_steps):
Eğer kullanıcı dosya/klasör oluşturma, silme veya müzik çalma gibi somut işlemler istiyorsa, 
"executable_steps" alanında bu adımları çalıştırılabilir formatta üret.

Kullanabileceğin aksiyonlar:
- create_file: Dosya oluştur. Params: {"path": "desktop/documents/downloads", "name": "dosya-adi"}
- create_folder: Klasör oluştur. Params: {"path": "desktop/documents/downloads", "name": "klasor-adi"}
- delete_file: Dosya sil. Params: {"path": "...", "name": "..."}
- delete_folder: Klasör sil. Params: {"path": "...", "name": "..."}
- play_music: Müzik çal. Params: {"song_name": "şarkı adı veya sanatçı"}
- web_search: İnternette ara. Params: {"name": "arama sorgusu"}

Path değerleri: desktop, documents, downloads, music, pictures veya klasör yolu (örn: "desktop/proje-klasoru")

JSON FORMAT:
{
  "type": "answer" | "plan" | "suggestion" | "empathy",
  "response": "Ana yanıt metni",
  "emotion_detected": "happy" | "sad" | "frustrated" | "curious" | "neutral" | null,
  "steps": ["adım 1", "adım 2", ...] (plan için, yoksa null),
  "executable_steps": [{"action": "...", "params": {...}}, ...] (çalıştırılabilir adımlar, yoksa null),
  "follow_up": "Takip sorusu veya öneri" (opsiyonel, yoksa null)
}

ÖRNEKLER:

User: "Python nedir?"
Output: {"type": "answer", "response": "Python, okunması kolay sözdizimi ile bilinen yüksek seviyeli bir programlama dilidir Efendim. Web geliştirme, veri analizi, yapay zeka ve otomasyon gibi birçok alanda kullanılır.", "emotion_detected": "curious", "steps": null, "executable_steps": null, "follow_up": "Python hakkında daha detaylı bilgi ister misiniz?"}

User: "Sıkıldım, ne yapayım?"
Output: {"type": "empathy", "response": "Sizi anlıyorum Efendim, bazen böyle hissedebiliriz. Size birkaç öneri sunabilirim.", "emotion_detected": "frustrated", "steps": null, "executable_steps": null, "follow_up": "Müzik dinlemek, kısa bir yürüyüş yapmak veya yeni bir hobi denemek iyi gelebilir. Hangisi ilginizi çeker?"}

User: "Bu projeyi nasıl organize edebilirim?"
Output: {"type": "plan", "response": "Projenizi organize etmek için şu adımları öneriyorum Efendim:", "emotion_detected": null, "steps": ["1. Projenin kapsamını ve hedeflerini belirleyin", "2. Görevleri küçük parçalara bölün", "3. Her görev için öncelik sırası belirleyin", "4. Zaman çizelgesi oluşturun", "5. İlerlemeyi düzenli takip edin"], "executable_steps": null, "follow_up": null}

User: "Masaüstüne yeni-proje adında klasör oluştur ve içine README dosyası aç"
Output: {"type": "plan", "response": "Masaüstüne yeni-proje klasörünü ve içine README dosyasını oluşturuyorum Efendim.", "emotion_detected": null, "steps": ["1. Masaüstüne yeni-proje klasörü oluştur", "2. Klasör içine README dosyası oluştur"], "executable_steps": [{"action": "create_folder", "params": {"path": "desktop", "name": "yeni-proje"}}, {"action": "create_file", "params": {"path": "desktop/yeni-proje", "name": "README"}}], "follow_up": null}

User: "Belgelerime iki klasör aç: notlar ve projeler"
Output: {"type": "plan", "response": "Belgelerinize notlar ve projeler klasörlerini oluşturuyorum Efendim.", "emotion_detected": null, "steps": ["1. notlar klasörü oluştur", "2. projeler klasörü oluştur"], "executable_steps": [{"action": "create_folder", "params": {"path": "documents", "name": "notlar"}}, {"action": "create_folder", "params": {"path": "documents", "name": "projeler"}}], "follow_up": null}

Sadece JSON ile yanıt ver, başka açıklama ekleme.
"""

# Varsayılan alanlar (setdefault için)
_DEFAULT_RESULT_FIELDS: dict[str, Any] = {
    "type": "answer",
    "response": "Efendim?",
    "emotion_detected": None,
    "steps": None,
    "executable_steps": None,
    "follow_up": None,
}


def _build_fallback_result(content: str, success: bool = True) -> dict[str, Any]:
    """
    JSON parse edilemediğinde ham yanıttan sonuç oluştur.

    Args:
        content: LLM'den gelen ham metin
        success: İşlemin başarılı sayılıp sayılmayacağı

    Returns:
        Standart sonuç dictionary
    """
    return {
        "type": "answer",
        "response": content,
        "emotion_detected": None,
        "steps": None,
        "executable_steps": None,
        "follow_up": None,
        "success": success,
    }


def process_reasoning(
    user_input: str, emotion_context: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Reasoning gerektiren istekleri işle.

    Args:
        user_input: Kullanıcı girdisi
        emotion_context: Router'dan gelen duygu bilgisi (opsiyonel)

    Returns:
        Reasoning sonucu dictionary
    """
    try:
        # Duygu bağlamını prompt'a ekle
        context_addition: str = ""
        if emotion_context and emotion_context.get("detected"):
            category: str = emotion_context.get("category", "neutral")
            keywords: list[str] = emotion_context.get("keywords", [])
            context_addition = (
                f"\n[BAĞLAM: Kullanıcı şu duyguları ifade ediyor: "
                f"{', '.join(keywords)}. Kategori: {category}]"
            )

        full_input: str = user_input + context_addition

        response = ollama.chat(
            model=REASONING_MODEL,
            messages=[
                {"role": "system", "content": REASONING_SYSTEM_PROMPT},
                {"role": "user", "content": full_input},
            ],
            options={"temperature": REASONING_TEMPERATURE},
        )

        content: str = response.message.content.strip()

        # JSON çıkar
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            logger.info("Reasoning JSON bulunamadı, ham yanıt kullanılıyor")
            return _build_fallback_result(content)

        # JSON parse etmeyi dene
        json_str: str = match.group()

        try:
            result: dict = json.loads(json_str)
        except json.JSONDecodeError:
            # Escape karakterlerini temizle ve tekrar dene
            cleaned: str = json_str.replace("\\", "\\\\")
            cleaned = re.sub(r'\\\\([^"\\nrtbfu])', r"\1", cleaned)

            try:
                result = json.loads(cleaned)
            except json.JSONDecodeError:
                logger.warning("JSON parse başarısız, ham yanıt kullanılıyor")
                return _build_fallback_result(content)

        result["success"] = True

        # Varsayılan alanları doldur
        for key, default_value in _DEFAULT_RESULT_FIELDS.items():
            result.setdefault(key, default_value)

        return result

    except ConnectionError as exc:
        logger.error("Ollama bağlantı hatası: %s", exc)
    except Exception as exc:
        logger.error("Reasoning Engine hatası: %s", exc, exc_info=True)

    return {
        "type": "error",
        "response": "Düşünme sürecinde bir hata oluştu Efendim.",
        "emotion_detected": None,
        "steps": None,
        "follow_up": None,
        "success": False,
    }


def format_reasoning_response(result: dict[str, Any]) -> str:
    """Reasoning sonucunu kullanıcıya gösterilecek formata çevir."""
    parts: list[str] = [result.get("response", "")]

    # Plan adımları varsa ekle
    steps: Optional[list] = result.get("steps")
    if steps and isinstance(steps, list):
        step_lines: str = "\n".join(f"  • {step}" for step in steps)
        parts.append(step_lines)

    # Takip sorusu varsa ekle
    follow_up: Optional[str] = result.get("follow_up")
    if follow_up:
        parts.append(follow_up)

    return "\n\n".join(parts)

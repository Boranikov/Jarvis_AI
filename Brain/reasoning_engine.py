"""
Jarvis AI - Reasoning Engine
qwen2.5:7b modeli ile düşünme, planlama ve duygu analizi.
Bu engine yalnızca gerektiğinde çağrılır.
"""

import ollama
import json
import re
from config import REASONING_MODEL, REASONING_TEMPERATURE

REASONING_SYSTEM_PROMPT = """
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
3. PLANLAMA: Karmaşık istekleri adımlara böl ve plan oluştur.
4. TAVSİYE: Önerilerde bulun, yardımcı ol.

JSON FORMAT:
{
  "type": "answer" | "plan" | "suggestion" | "empathy",
  "response": "Ana yanıt metni",
  "emotion_detected": "happy" | "sad" | "frustrated" | "curious" | "neutral" | null,
  "steps": ["adım 1", "adım 2", ...] (plan için, yoksa null),
  "follow_up": "Takip sorusu veya öneri" (opsiyonel, yoksa null)
}

ÖRNEKLER:

User: "Python nedir?"
Output: {"type": "answer", "response": "Python, okunması kolay sözdizimi ile bilinen yüksek seviyeli bir programlama dilidir Efendim. Web geliştirme, veri analizi, yapay zeka ve otomasyon gibi birçok alanda kullanılır.", "emotion_detected": "curious", "steps": null, "follow_up": "Python hakkında daha detaylı bilgi ister misiniz?"}

User: "Sıkıldım, ne yapayım?"
Output: {"type": "empathy", "response": "Sizi anlıyorum Efendim, bazen böyle hissedebiliriz. Size birkaç öneri sunabilirim.", "emotion_detected": "frustrated", "steps": null, "follow_up": "Müzik dinlemek, kısa bir yürüyüş yapmak veya yeni bir hobi denemek iyi gelebilir. Hangisi ilginizi çeker?"}

User: "Bu projeyi nasıl organize edebilirim?"
Output: {"type": "plan", "response": "Projenizi organize etmek için şu adımları öneriyorum Efendim:", "emotion_detected": null, "steps": ["1. Projenin kapsamını ve hedeflerini belirleyin", "2. Görevleri küçük parçalara bölün", "3. Her görev için öncelik sırası belirleyin", "4. Zaman çizelgesi oluşturun", "5. İlerlemeyi düzenli takip edin"], "follow_up": null}

Sadece JSON ile yanıt ver, başka açıklama ekleme.
"""


def process_reasoning(user_input: str, emotion_context: dict = None) -> dict:
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
        context_addition = ""
        if emotion_context and emotion_context.get("detected"):
            category = emotion_context.get("category", "neutral")
            keywords = emotion_context.get("keywords", [])
            context_addition = f"\n[BAĞLAM: Kullanıcı şu duyguları ifade ediyor: {', '.join(keywords)}. Kategori: {category}]"
        
        full_input = user_input + context_addition
        
        response = ollama.chat(
            model=REASONING_MODEL,
            messages=[
                {"role": "system", "content": REASONING_SYSTEM_PROMPT},
                {"role": "user", "content": full_input}
            ],
            options={"temperature": REASONING_TEMPERATURE}
        )
        
        content = response.message.content.strip()
        
        # JSON çıkar
        match = re.search(r"\{.*\}", content, re.DOTALL)
        
        if not match:
            return {
                "type": "answer",
                "response": content,
                "emotion_detected": None,
                "steps": None,
                "follow_up": None,
                "success": True
            }
        
        result = json.loads(match.group())
        result["success"] = True
        
        # Varsayılan alanları doldur
        result.setdefault("type", "answer")
        result.setdefault("response", "Efendim?")
        result.setdefault("emotion_detected", None)
        result.setdefault("steps", None)
        result.setdefault("follow_up", None)
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Reasoning Engine: {str(e)}")
        return {
            "type": "error",
            "response": "Düşünme sürecinde bir hata oluştu Efendim.",
            "emotion_detected": None,
            "steps": None,
            "follow_up": None,
            "success": False
        }


def format_reasoning_response(result: dict) -> str:
    """
    Reasoning sonucunu kullanıcıya gösterilecek formata çevir.
    
    Args:
        result: process_reasoning sonucu
        
    Returns:
        Formatlanmış yanıt string'i
    """
    response = result.get("response", "")
    steps = result.get("steps")
    follow_up = result.get("follow_up")
    
    output = response
    
    # Plan adımları varsa ekle
    if steps and isinstance(steps, list):
        output += "\n"
        for step in steps:
            output += f"\n  • {step}"
    
    # Takip sorusu varsa ekle
    if follow_up:
        output += f"\n\n{follow_up}"
    
    return output

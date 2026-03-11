"""
Jarvis AI - Intent Engine

Kullanıcı girdisini analiz ederek intent türü, aksiyon ve parametreleri çıkarır.
"""

import json
from typing import Any

import ollama

from Config.config import FAST_MODEL, get_logger

logger = get_logger("brain.intent")

SYSTEM_PROMPT: str = """
Sen Jarvis'in intent anlama katmanısın. Görevin YALNIZCA kullanıcının ne yapmak istediğini anlamak ve JSON döndürmek.

Yanıtın HER ZAMAN geçerli bir JSON objesi olmalıdır. Başka hiçbir şey ekleme.

=== TYPE KURALLARI ===
"type" alanı şu değerlerden birini alır:

- "skill"     → Dosya/klasör işlemleri, müzik, web arama gibi direkt aksiyonlar
- "coding"    → Kod yazma, debug, refactor, script oluşturma
- "reasoning" → Soru cevaplama, açıklama, planlama, tavsiye, duygu içeren konuşma
- "chat"      → Selamlama, "nasılsın", "orada mısın" gibi basit sohbet

=== ALLOWED ACTIONS (sadece type="skill" için) ===
create_file, create_folder, delete_file, delete_folder,
write_to_file, read_file, list_dir_recursive,
play_specific_music, play_emotion_music, pause_music, resume_music, next_track, get_current_track,
web_search, small_talk, missing_parameters, unknown, multi_action

=== GENEL KURALLAR ===
- type="coding" veya "reasoning" ise action="none", params={} bırak.
- Jarvis, robot gibi kelimeleri parametre olarak alma.
- Eksik parametre varsa: action="missing_parameters", original_action=asıl_aksiyon, params.missing=[eksik_alanlar]

=== PARAMETRE ÇIKARMA ===
- "name": Kullanıcı açıkça belirtirse al. Türkçe ekleri temizle ("projeyi" → "proje").
- "path": masaüstü/masaüstüne → "desktop", belgeler → "documents", indirilenler → "downloads"
- Dosya/klasör işlemlerinde path belirtilmemişse path=null bırak (handler tamamlar).
- play_music: Sanatçı, şarkı adı veya aranacak kelime. "Tarkan çal" → artist_name="tarkan", query="tarkan". "sezen aksu zalim" → artist_name="sezen aksu", song_name="zalim".

=== MULTI-ACTION ===
Birden fazla görev varsa: action="multi_action", actions listesini doldur.
Her action: {"action": "...", "path": "...", "name": "...", "parameters": {}}
write_to_file içeriyorsa type="coding" kullan, intent engine değil coding engine halleder.

=== JSON FORMATI ===
{
  "type": "skill | coding | reasoning | chat",
  "action": "string",
  "path": "string or null",
  "name": "string or null",
  "song_name": "string or null",
  "artist_name": "string or null",
  "query": "string or null",
  "original_action": "string or null",
  "confidence": 0.0-1.0,
  "parameters": {},
  "actions": []
}

=== ÖRNEKLER ===

User: "Masaüstüne proje klasörü aç"
{"type":"skill","action":"create_folder","path":"desktop","name":"proje","song_name":null,"artist_name":null,"query":null,"original_action":null,"confidence":0.98,"parameters":{},"actions":[]}

User: "Belgelerime klasör oluştur"
{"type":"skill","action":"missing_parameters","path":"documents","name":null,"song_name":null,"artist_name":null,"query":null,"original_action":"create_folder","confidence":0.95,"parameters":{"missing":["name"]},"actions":[]}

User: "Tarkan çal"
{"type":"skill","action":"play_music","path":null,"name":null,"song_name":null,"artist_name":"tarkan","query":"tarkan","original_action":null,"confidence":0.99,"parameters":{},"actions":[]}

User: "Python nedir?"
{"type":"reasoning","action":"none","path":null,"name":null,"song_name":null,"artist_name":null,"query":null,"original_action":null,"confidence":0.97,"parameters":{},"actions":[]}

User: "Hesap makinesi kodu yaz"
{"type":"coding","action":"none","path":null,"name":null,"song_name":null,"artist_name":null,"query":null,"original_action":null,"confidence":0.99,"parameters":{},"actions":[]}

User: "Nasılsın Jarvis"
{"type":"chat","action":"small_talk","path":null,"name":null,"song_name":null,"artist_name":null,"query":null,"original_action":null,"confidence":0.99,"parameters":{},"actions":[]}

User: "Masaüstüne deneme klasörü oluştur ve içine hesap_makinesi.py yaz"
{"type":"coding","action":"multi_action","path":null,"name":null,"song_name":null,"artist_name":null,"query":null,"original_action":null,"confidence":0.96,"parameters":{},"actions":[{"action":"create_folder","path":"desktop","name":"deneme","parameters":{}},{"action":"write_to_file","path":"desktop/deneme","name":"hesap_makinesi.py","parameters":{}}]}

SADECE JSON DÖNDÜR.
"""

# Varsayılan (boş/hata) yanıt şablonu
_DEFAULT_FIELDS: dict[str, Any] = {
    "type": "chat",
    "path": None,
    "name": None,
    "song_name": None,
    "artist_name": None,
    "query": None,
    "original_action": None,
    "confidence": 0.0,
    "parameters": {},
    "actions": [],
}


def process_command(text: str, history: list[dict]) -> dict[str, Any]:
    """
    Kullanıcı komutunu işle ve intent'i tanı.

    Args:
        text: Kullanıcı girdisi
        history: Konuşma geçmişi

    Returns:
        Intent ve parametreleri içeren dictionary
    """
    # Son 3 konuşmayı geçmiş olarak ekle
    history_msgs: list[dict] = []
    for entry in history[-3:]:
        history_msgs.append({"role": "user", "content": entry.get("user", "")})
        history_msgs.append({
            "role": "assistant",
            "content": entry.get("jarvis", ""),
        })

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history_msgs,
        {"role": "user", "content": text},
    ]

    try:
        response = ollama.chat(
            model=FAST_MODEL,
            messages=messages,
            format="json",
            options={"temperature": 0.0},
        )

        result: dict = json.loads(response.message.content)
        for key, default_value in _DEFAULT_FIELDS.items():
            result.setdefault(key, default_value)

        logger.debug(
            "Intent: type=%s action=%s confidence=%.2f",
            result.get("type"),
            result.get("action"),
            result.get("confidence", 0.0),
        )

        return result

    except json.JSONDecodeError as exc:
        logger.error("JSON parse hatası (format=json ile olmamalı): %s", exc)
    except ConnectionError as exc:
        logger.error("Ollama bağlantı hatası: %s", exc)
    except Exception as exc:
        logger.error("Intent Engine beklenmeyen hata: %s", exc, exc_info=True)

    return {
        "type": "chat",
        "action": "unknown",
        **{k: v for k, v in _DEFAULT_FIELDS.items() if k != "type"},
    }

"""
Jarvis AI - Intent Engine

Kullanıcı girdisini NLP ile analiz ederek aksiyon ve parametreleri çıkarır.
"""

import json
import re
from typing import Any

import ollama

from config import FAST_MODEL, LLM_TEMPERATURE, get_logger

logger = get_logger("brain.intent")

SYSTEM_PROMPT: str = """
You are Jarvis, a local Turkish AI assistant.

Rules:
- Always respond in Turkish.
- Always address the user as "Efendim".
- Respond ONLY with valid JSON.
- No explanations, no markdown code blocks, just raw JSON.
- Be concise and helpful.

Allowed actions:
- create_file
- create_folder
- delete_file
- delete_folder
- play_music
- web_search
- small_talk
- missing_parameters
- unknown

IMPORTANT:
- Do NOT take your name ("Jarvis", "robot" etc.) as a parameter.
- If required parameters are missing for an action (e.g., create_folder needs a name):
  * action = "missing_parameters"
  * original_action = the intended action (e.g., "create_folder")
  * parameters.missing = list of missing fields ["name"]

Parameter Extraction Rules:
- ONLY extract "name" if the user explicitly provides it.
- Remove suffixes from the name (e.g. "projeyi" -> "proje", "dosyası" -> "dosya").
- Keywords like "klasör", "dosya", "müzik" are TYPES, NOT names.
- Location keywords are PATHS, NOT names.
- "masaüstüne klasör aç" -> path="desktop", name=null (Action: missing_parameters).
- "deneme klasörü aç" -> path=null, name="deneme" (Action: create_folder).
- For play_music: Put the COMPLETE query (artist + song name) into song_name. Do NOT separate them.
  * "tarkan çal" -> song_name="tarkan"
  * "experience çal" -> song_name="experience"
  * "spotifydan tarkan çal" -> song_name="tarkan"
  * "Everyway that i can çal" -> song_name="everyway that i can"
  * "tarkan dudu dudu çal" -> song_name="tarkan dudu dudu"
  * "sezen aksu zalim çal" -> song_name="sezen aksu zalim"
  * "ahmet kaya kendine iyi bak çal" -> song_name="ahmet kaya kendine iyi bak"
  * "dudu çal" -> song_name="dudu"
  * "where have you been çal" -> song_name="where have you been"

Locations (Path Keywords):
- masaüstü, masaüstüne, masaüstümde -> desktop
- belgeler, belgelerim, belgelere -> documents
- indirilenler, indirilenlere -> downloads
- müzik, müzikler -> music
- resimler, fotoğraflar -> pictures

JSON FORMAT:
{
  "action": "string",
  "reply": "string in Turkish",
  "path": "string or null",
  "name": "string or null",
  "original_action": "string or null",
  "song_name": "string or null",
  "parameters": {}
}

EXAMPLES:

User: "Masaüstüne yeni proje adında bir klasör aç"
Output: {"action": "create_folder", "reply": "Masaüstüne yeni proje klasörünü oluşturuyorum Efendim.", "path": "desktop", "name": "yeni proje", "original_action": null, "parameters": {}}

User: "Belgelerime klasör oluştur"
Output: {"action": "missing_parameters", "reply": "Klasörün ismini belirtmediniz Efendim.", "path": "documents", "name": null, "original_action": "create_folder", "parameters": {"missing": ["name"]}}

User: "Tarkan çal"
Output: {"action": "play_music", "reply": "Tarkan'ı Spotify'da arıyorum Efendim.", "path": null, "name": null, "song_name": "tarkan", "original_action": null, "parameters": {}}

User: "Tarkan Dudu Dudu çal"
Output: {"action": "play_music", "reply": "Tarkan - Dudu Dudu şarkısını Spotify'da arıyorum Efendim.", "path": null, "name": null, "song_name": "tarkan dudu dudu", "original_action": null, "parameters": {}}

User: "Nasılsın Jarvis"
Output: {"action": "small_talk", "reply": "İyiyim, teşekkürler Efendim. Size nasıl yardımcı olabilirim?", "path": null, "name": null, "original_action": null, "parameters": {}}

User: "Jarvis pyton nedir araştır"
Output: {"action": "web_search", "reply": "Python nedir araştırıyorum Efendim.", "path": null, "name": "python nedir", "original_action": null, "parameters": {}}

Respond ONLY with JSON.
"""

# Varsayılan (boş/hata) yanıt şablonu
_DEFAULT_FIELDS: dict[str, Any] = {
    "path": None,
    "name": None,
    "song_name": None,
    "original_action": None,
    "parameters": {},
    "reply": "Efendim?",
}


def process_command(text: str, history: list[dict]) -> dict[str, Any]:
    """
    Kullanıcı komutunu NLP ile işle ve intent'i tanı.

    Args:
        text: Kullanıcı girdisi
        history: Konuşma geçmişi

    Returns:
        Intent ve parametreleri içeren dictionary
    """
    try:
        response = ollama.chat(
            model=FAST_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            options={"temperature": LLM_TEMPERATURE},
        )

        content: str = response.message.content.strip()
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            logger.warning("JSON bulunamadı, LLM yanıtı: %.100s", content)
            return {
                "action": "unknown",
                "reply": "Anlayamadım efendim.",
                "parameters": {},
            }

        result: dict = json.loads(match.group())

        # Eksik alanları varsayılanlarla doldur
        for key, default_value in _DEFAULT_FIELDS.items():
            result.setdefault(key, default_value)

        return result

    except json.JSONDecodeError as exc:
        logger.error("JSON parse hatası: %s", exc)
    except ConnectionError as exc:
        logger.error("Ollama bağlantı hatası: %s", exc)
    except Exception as exc:
        # Beklenmeyen hatalar için son savunma hattı
        logger.error("Intent Engine beklenmeyen hata: %s", exc, exc_info=True)

    return {
        "action": "unknown",
        "reply": "Bir hata oluştu efendim.",
        "path": None,
        "name": None,
        "original_action": None,
        "parameters": {},
    }

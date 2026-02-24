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
- write_to_file
- read_file
- list_dir_recusive
- play_music
- pause_music
- web_search
- small_talk
- missing_parameters
- unknown
- multi_action  (use when user gives multiple tasks in one sentence)

IMPORTANT:
- Do NOT take your name ("Jarvis", "robot" etc.) as a parameter.
- If required parameters are missing for an action (e.g., create_folder needs a name):
  * action = "missing_parameters"
  * original_action = the intended action (e.g., "create_folder")
  * parameters.missing = list of missing fields ["name"]

Parameter Extraction Rules:
- ONLY extract "name" if the user explicitly provides it.
- Remove suffixes from the name (e.g. "projeyi" -> "proje", "dosyası" -> "dosya").
- For file extensions: keep them (e.g. "hesap_makinesi.py" stays "hesap_makinesi.py").
- Keywords like "klasör", "dosya", "müzik" are TYPES, NOT names.
- Location keywords are PATHS, NOT names.
- "masaüstüne klasör aç" -> path="desktop", name=null (Action: missing_parameters).
- "deneme klasörü aç" -> path=null, name="deneme" (Action: create_folder).
- For play_music: Put the COMPLETE query (artist + song name) into song_name. Do NOT separate them.
  * "tarkan çal" -> song_name="tarkan"
  * "tarkan dudu dudu çal" -> song_name="tarkan dudu dudu"
  * "sezen aksu zalim çal" -> song_name="sezen aksu zalim"

Locations (Path Keywords):
- masaüstü, masaüstüne, masaüstümde -> desktop
- belgeler, belgelerim, belgelere -> documents
- indirilenler, indirilenlere -> downloads
- müzik, müzikler -> music
- resimler, fotoğraflar -> pictures

MULTI-ACTION RULES:
- When the user asks for multiple tasks in one sentence, use action="multi_action" and list all steps in "actions" array.
- Each action in "actions" must have: {"action": "...", "path": "...", "name": "...", "parameters": {}}
- For write_to_file: include "content" inside "parameters" with the COMPLETE, REAL, WORKING code.
  * STRICTLY FORBIDDEN: Using "..." or "# placeholder" or incomplete code as content.
  * STRICTLY FORBIDDEN: Leaving content as a comment-only stub like "# ATM Kodu\n...".
  * REQUIRED: Write the FULL, working Python code from top to bottom. Every function must be implemented.
- Path for a file inside a folder: use the folder name as part of path (e.g. "desktop/deneme").
- Order steps logically: create parent folder first, then write content directly (write_to_file creates the file automatically).

JSON FORMAT (single action):
{
  "action": "string",
  "reply": "string in Turkish",
  "path": "string or null",
  "name": "string or null",
  "original_action": "string or null",
  "song_name": "string or null",
  "query": "string or null",
  "parameters": {},
  "actions": []
}

JSON FORMAT (multi-action):
{
  "action": "multi_action",
  "reply": "string in Turkish summarizing all tasks",
  "path": null,
  "name": null,
  "original_action": null,
  "song_name": null,
  "query": null,
  "parameters": {},
  "actions": [
    {"action": "create_folder", "path": "desktop", "name": "deneme", "parameters": {}},
    {"action": "create_file", "path": "desktop/deneme", "name": "hesap_makinesi.py", "parameters": {}},
    {"action": "write_to_file", "path": "desktop/deneme", "name": "hesap_makinesi.py", "parameters": {"content": "# Hesap Makinesi\n..."}}
  ]
}

EXAMPLES:

User: "Masaüstüne yeni proje adında bir klasör aç"
Output: {"action": "create_folder", "reply": "Masaüstüne yeni proje klasörünü oluşturuyorum Efendim.", "path": "desktop", "name": "yeni proje", "original_action": null, "parameters": {}, "actions": []}

User: "Belgelerime klasör oluştur"
Output: {"action": "missing_parameters", "reply": "Klasörün ismini belirtmediniz Efendim.", "path": "documents", "name": null, "original_action": "create_folder", "parameters": {"missing": ["name"]}, "actions": []}

User: "Masaüstüne deneme klasörü oluştur ve içine hesap_makinesi.py adlı hesap makinesi kodu yaz"
Output: {"action": "multi_action", "reply": "Masaüstünde deneme klasörünü oluşturuyorum ve içine hesap_makinesi.py dosyasını yazıyorum Efendim.", "path": null, "name": null, "original_action": null, "song_name": null, "query": null, "parameters": {}, "actions": [{"action": "create_folder", "path": "desktop", "name": "deneme", "parameters": {}}, {"action": "write_to_file", "path": "desktop/deneme", "name": "hesap_makinesi.py", "parameters": {"content": "def topla(a, b):\n    return a + b\n\ndef cikar(a, b):\n    return a - b\n\ndef carp(a, b):\n    return a * b\n\ndef bol(a, b):\n    if b == 0:\n        return 'Sifira bolme hatasi'\n    return a / b\n\nif __name__ == '__main__':\n    print('=== Hesap Makinesi ===')\n    a = float(input('Birinci sayi: '))\n    op = input('Islem (+, -, *, /): ')\n    b = float(input('Ikinci sayi: '))\n    if op == '+': print('Sonuc:', topla(a, b))\n    elif op == '-': print('Sonuc:', cikar(a, b))\n    elif op == '*': print('Sonuc:', carp(a, b))\n    elif op == '/': print('Sonuc:', bol(a, b))\n    else: print('Gecersiz islem')\n"}}]}

User: "Tarkan çal"
Output: {"action": "play_music", "reply": "Tarkan'ı Spotify'da arıyorum Efendim.", "path": null, "name": null, "song_name": "tarkan", "original_action": null, "parameters": {}, "actions": []}

User: "Şarkıyı durdur"
Output: {"action": "pause_music", "reply": "Müziği durduruyorum Efendim.", "path": null, "name": null, "original_action": null, "parameters": {}, "actions": []}

User: "Müziği devam ettir"
Output: {"action": "resume_music", "reply": "Müziği devam ettiriyorum Efendim.", "path": null, "name": null, "original_action": null, "parameters": {}, "actions": []}

User: "Şu an ne çalıyor"
Output: {"action": "get_current_track", "reply": "Şu an çalan şarkı bilgisini getiriyorum Efendim.", "path": null, "name": null, "original_action": null, "parameters": {}, "actions": []}

User: "Nasılsın Jarvis"
Output: {"action": "small_talk", "reply": "İyiyim, teşekkürler Efendim. Size nasıl yardımcı olabilirim?", "path": null, "name": null, "original_action": null, "parameters": {}, "actions": []}

RESPOND ONLY WITH JSON.
"""

# Varsayılan (boş/hata) yanıt şablonu
_DEFAULT_FIELDS: dict[str, Any] = {
    "path": None,
    "name": None,
    "song_name": None,
    "query": None,
    "original_action": None,
    "parameters": {},
    "actions": [],
    "reply": "Efendim?",
}

# JSON format düzeltme prompt'u — model sohbet moduna girince kullanılır
_FORMAT_CORRECTION_PROMPT: str = (
    "HATA: Yanıtın JSON formatında değildi. "
    "Cevabını YALNIZCA şu formatta ver, başka hiçbir şey ekleme:\n"
    '{"action": "...", "reply": "...", "path": null, "name": null, '
    '"song_name": null, "query": null, "original_action": null, "parameters": {}}'
)

def _sanitize_json_string(raw: str) -> str:
    """
    JSON string değerlerinin içindeki literal kontrol karakterlerini kaçır.

    LLM bazen code content için gerçek newline (\n) yazar, JSON geçerli \\n bekler.
    Bu fonksiyon JSON yapısını bozmadan, yalnızca string literal içindeki
    kontrol karakterlerini düzeltir.
    """
    result: list[str] = []
    in_string: bool = False
    escape_next: bool = False

    for char in raw:
        if escape_next:
            result.append(char)
            escape_next = False
        elif char == "\\":
            result.append(char)
            escape_next = True
        elif char == '"':
            in_string = not in_string
            result.append(char)
        elif in_string:
            if char == "\n":
                result.append("\\n")
            elif char == "\r":
                result.append("\\r")
            elif char == "\t":
                result.append("\\t")
            else:
                result.append(char)
        else:
            result.append(char)

    return "".join(result)


def process_command(text: str, history: list[dict]) -> dict[str, Any]:
    """
    Kullanıcı komutunu NLP ile işle ve intent'i tanı.

    Args:
        text: Kullanıcı girdisi
        history: Konuşma geçmişi

    Returns:
        Intent ve parametreleri içeren dictionary
    """
    # Asistan yanıtlarını [JSON_RESPONSE] etiketiyle sarıyoruz.
    # Böylece model, önceki doğal dil yanıtlarını görüp sohbet moduna girmiyor.
    history_msgs: list[dict] = []
    for entry in history[-3:]:
        history_msgs.append({"role": "user", "content": entry.get("user", "")})
        history_msgs.append({
            "role": "assistant",
            "content": f"[JSON_RESPONSE] {entry.get('jarvis', '')}",
        })

    base_messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history_msgs,
        {"role": "user", "content": text},
    ]

    try:
        response = ollama.chat(
            model=FAST_MODEL,
            messages=base_messages,
            options={"temperature": LLM_TEMPERATURE},
        )
        content: str = response.message.content.strip()
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            # --- JSON bulunamadı: tek seferlik retry ---
            logger.warning("JSON bulunamadı, retry deneniyor. LLM yanıtı: %.100s", content)
            retry_messages = base_messages + [
                {"role": "assistant", "content": content},
                {"role": "user", "content": _FORMAT_CORRECTION_PROMPT},
            ]
            retry_response = ollama.chat(
                model=FAST_MODEL,
                messages=retry_messages,
                options={"temperature": 0.0},  # Deterministik → JSON gelmek zorunda
            )
            retry_content: str = retry_response.message.content.strip()
            match = re.search(r"\{.*\}", retry_content, re.DOTALL)

            if not match:
                logger.error("Retry sonrası da JSON bulunamadı: %.100s", retry_content)
                return {
                    "action": "unknown",
                    "reply": "Anlayamadım efendim.",
                    **{k: v for k, v in _DEFAULT_FIELDS.items() if k != "reply"},
                }
            content = retry_content
            match = re.search(r"\{.*\}", content, re.DOTALL)

        raw_json: str = _sanitize_json_string(match.group())
        result: dict = json.loads(raw_json)

        # Eksik alanları varsayılanlarla doldur
        for key, default_value in _DEFAULT_FIELDS.items():
            result.setdefault(key, default_value)

        return result

    except json.JSONDecodeError as exc:
        logger.error("JSON parse hatası: %s", exc)
    except ConnectionError as exc:
        logger.error("Ollama bağlantı hatası: %s", exc)
    except Exception as exc:
        logger.error("Intent Engine beklenmeyen hata: %s", exc, exc_info=True)

    return {
        "action": "unknown",
        "reply": "Bir hata oluştu efendim.",
        "path": None,
        "name": None,
        "original_action": None,
        "parameters": {},
    }

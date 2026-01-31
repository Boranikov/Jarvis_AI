"""
Jarvis Intent Engine
Kullanıcı girdisini NLP ile analiz ederek aksiyon ve parametreleri çıkar.
"""

import ollama
import json
import re
from config import LLM_MODEL, LLM_TEMPERATURE

SYSTEM_PROMPT = """
You are name is Jarvis, a local Turkish AI assistant.

Rules:
- Always respond in Turkish
- Always address the user as "Efendim"
- Respond ONLY with valid JSON
- No explanations, no markdown
- Be concise and helpful

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
- You NEVER ask questions
- If required parameters are missing:
- Do NOT take your name as a parameter
  * action = "missing_parameters"
  * original_action = the actual action that needs parameters
  * parameters.missing = list of missing fields

Parameter Extraction Rules:
- ONLY extract "name" if the user explicitly provides it
- "klasör", "dosya", "müzik" etc are ACTION KEYWORDS, NOT names
- If user says "klasör oluştur" WITHOUT specifying name → name is MISSING
- If user says "test.txt oluştur" → name = "test.txt"
- If user says "müzik.mp3 sil" → name = "müzik.mp3"

Locations:
- masaüstü → desktop
- belgeler → documents
- indirilenler → downloads
- müzik → music
- resimler → pictures

JSON FORMAT:
{
  "action": "string",
  "reply": "string in Turkish",
  "parameters": {} or {"missing": ["field1", "field2"]},
  "path": "string or null",
  "name": "string or null",
  "original_action": "string or null"
}

Respond ONLY with JSON.
"""


def process_command(text: str, history: list) -> dict:
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
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            options={"temperature": LLM_TEMPERATURE}
        )

        content = response.message.content.strip()
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            return {
                "action": "unknown",
                "reply": "Anlayamadım efendim.",
                "parameters": {}
            }

        result = json.loads(match.group())

        # Yanıta "Efendim" ekle eğer yoksa
        if "reply" in result and "efendim" not in result["reply"].lower():
            result["reply"] += " Efendim."

        return result

    except Exception as e:
        print(f"[ERROR] Intent Engine: {str(e)}")
        return {
            "action": "unknown",
            "reply": "Bir hata oluştu efendim.",
            "parameters": {}
        }


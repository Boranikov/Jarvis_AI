import ollama
import json
import re

SYSTEM_PROMPT = """
You are Jarvis, a local AI assistant.

Rules:
- Always respond in Turkish
- Always address the user as "Efendim"
- Respond ONLY with valid JSON
- No explanations
- No markdown

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
- You NEVER ask questions.
- If required parameters are missing:
  action = "missing_parameters"
  parameters.missing = list of missing fields

Parameter rules:
- create_file / create_folder require "name"
- If extension missing → add ".txt"
- Default location = "desktop"

Locations:
- masaüstü → desktop
- belgeler → documents
- indirilenler → downloads
- müzik → music
- resimler → pictures

JSON FORMAT:
{
  "action": "string",
  "reply": "string",
  "parameters": {}
}

Respond ONLY with JSON.
"""

def process_command(text, history):
    response = ollama.chat(
        model="gemma2:2b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        options={"temperature": 0.1}
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

    if "reply" in result and "efendim" not in result["reply"].lower():
        result["reply"] += " Efendim."

    return result

import ollama
import json
import re

def process_command(text):
    prompt = f"""
Sen Türkçe konuşan yardımsever bir asistansın.
GÖREV: Kullanıcının cümlesine göre bir 'action' belirle ve ona Türkçe bir 'reply' (cevap) ver.
SADECE aşağıdaki JSON formatında çıktı ver. Başka hiçbir şey yazma.

Action Listesi: ["play_music", "web_search", "create_folder", "small_talk", "unknown"]

Kullanıcı: "{text}"

Örnek JSON:
{{
    "action": "small_talk",
    "reply": "Sizin için her zaman efendim"
}}
"""
    try:
        # Llama 3.2 
        response = ollama.chat(
            model="llama3.2",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.3} # yaratıcılık
        )
        
        content = response.message.content.strip()
        
        # Temizlik
        json_match = re.search(r'(\{.*?\})', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
            
        return json.loads(content)

    except Exception as e:
        print(f"Hata: {e}")
        return {"action": "unknown", "reply": "Bir hata oluştu."}
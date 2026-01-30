import ollama
import json
import re

def process_command(text, history=[]):
    
    # --- 1. SABİT CEVAPLAR (Hız için) ---
    normalized_text = text.lower().strip()
    
    if "orda mısın" in normalized_text or "orada mısın" in normalized_text:
        return {"action": "small_talk", "reply": "Sizin için her zaman efendim.", "parameters": {}}
        
    if normalized_text in ["merhaba", "selam", "günaydın"]:
        return {"action": "small_talk", "reply": "Merhabalar efendim.", "parameters": {}}

    # --- 2. YAPAY ZEKA ---
    # Geçmişi metne dök
    history_text = ""
    for msg in history[-2:]: 
        history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
GÖREV: Kullanıcı girdisini analiz et ve JSON döndür.
BAĞLAM: Sen bilgisayar kontrol eden bir asistansın.

GEÇMİŞ:
{history_text}

KOMUTLAR VE ANLAMLARI:
- "create_file": Metin belgesi, txt, not defteri, dosya oluşturmak için.
- "create_folder": Klasör, dizin, dosya grubu oluşturmak için.
- "play_music": Şarkı, müzik, sanatçı çalmak için.
- "web_search": İnternet araması için.

ÖRNEKLER (BUNLARA BAKARAK CEVAPLA):
1. Kullanıcı: "Masaüstüne notlar adında bir txt dosyası oluştur."
   Çıktı: {{ "action": "create_file", "parameters": {{ "name": "notlar.txt", "location": "desktop" }}, "reply": "Notlar dosyası oluşturuluyor efendim." }}

2. Kullanıcı: "Resimler diye bir klasör aç."
   Çıktı: {{ "action": "create_folder", "parameters": {{ "name": "Resimler", "location": "desktop" }}, "reply": "Klasör açıldı efendim." }}

ŞU ANKİ GİRDİ: "{text}"

KURAL: "reply" mutlaka "Efendim" içermeli ve kibar olmalı.

SADECE JSON DÖNDÜR:
"""
    try:
        response = ollama.chat(
            model="gemma2:2b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1} # Yaratıcılığı kıstık, kurallara uysun
        )
        content = response.message.content.strip()
        
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        result = {}
        
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            try:
                result = json.loads(content)
            except:
                result = {"action": "unknown", "reply": "Tam anlayamadım efendim."}

        # Eksik reply kontrolü
        if "reply" not in result:
            result["reply"] = "İşleminiz yapılıyor efendim."
            
        return result

    except Exception as e:
        print(f"[HATA] {e}")
        return {"action": "unknown", "reply": "Sistem hatası efendim.", "parameters": {}}
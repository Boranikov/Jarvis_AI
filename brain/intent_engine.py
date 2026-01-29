import ollama
import json
import re

def process_command(text):
    prompt = f"""
Sen niyet analizi yapan gelişmiş bir yapay zeka motorusun.
GÖREV: Kullanıcının doğal dildeki isteğini analiz et ve aşağıdaki araçlardan (actions) hangisini kullanmak istediğini "anlamına göre" belirle.

MEVCUT AKSİYONLAR VE TANIMLARI:
1. "play_music": Kullanıcı şarkı dinlemek, müzik açmak veya bir sanatçıdan bir parça duymak istediğinde seç.
2. "create_folder": Kullanıcı yeni bir klasör/dizin oluşturmak istediğinde seç.
3. "delete_folder": Kullanıcı var olan bir klasörü silmek/kaldırmak istediğinde seç.
4. "create_file": Kullanıcı yeni bir dosya (txt, docx vb.) yaratmak istediğinde seç.
5. "delete_file": Kullanıcı bir dosyayı silmek istediğinde seç.
6. "web_search": Kullanıcı bir bilgi aradığında, internette bir şeye bakmak istediğinde veya "kimdir, nedir" diye sorduğunda seç.
7. "small_talk": Kullanıcı sadece selam veriyorsa, hal hatır soruyorsa veya işlem gerektirmeyen sohbet ediyorsa seç.

ÇIKTI FORMATI (JSON):
{{
    "action": "Yukarıdaki listeden en uygun olanı seç",
    "parameters": {{
        "name": "İşlem yapılacak dosya, klasör veya şarkı adı (Örn: 'Sezen Aksu', 'Ödevler', 'not.txt'). Bulamazsan null yap.",
        "location": "Sadece şunlardan biri: ['desktop', 'documents', 'downloads', 'music', 'pictures']. Kullanıcı belirtmediyse varsayılan 'desktop' seç."
    }},
    "reply": "Kullanıcıya işlemin yapıldığına dair Türkçe, kısa ve doğal bir onay mesajı, efendim diye hitap ederek."
}}

Kullanıcı Girdisi: "{text}"

SADECE JSON DÖNDÜR:
"""
    try:
        response = ollama.chat(
            model="gemma2:2b",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1} # Yaratıcılığı düşük tutuyoruz ki JSON bozulmasın
        )
        content = response.message.content.strip()
        
        # JSON'u ayıklama
        json_match = re.search(r'(\{.*\})', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        return json.loads(content)

    except Exception as e:
        print(f"[HATA] Model: {e}")
        return {"action": "unknown", "reply": "Ne demek istediğini tam anlayamadım.", "parameters": {}}
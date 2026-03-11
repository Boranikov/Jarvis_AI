"""
Jarvis AI - Native Tool Calling Test
Faz 1.3 & 1.4 Kapsamında izole test ortamı.
"""

import pprint
from typing import Any
import ollama

from Config.config import FAST_MODEL
from Skills.skills_manager import get_tool_schemas, perform_skill

# Adım 1.4: Yeni İç Ses (Inner Monologue) System Prompt'u
SYSTEM_PROMPT = """
Sen Jarvis isimli gelişmiş bir yapay zeka asistanısın.
Artık kullanıcının isteklerini yerine getirmek için doğrudan "tools" (araçlar) kullanabilirsin.

KURAL 1 (Düşünce Zinciri - Inner Monologue):
Herhangi bir aracı çağırmadan hemen önce, adım adım ne yapman gerektiğini sesli düşünmelisin.
Bunu normal yanıtının içine "Düşünce: [Düşüncen]" formatında yazabilirsin, ardından uygun aracı (tool_call) tetikle.

KURAL 2:
Eğer kullanıcının isteğini yerine getirmek için elinde uygun bir araç varsa, SADECE o aracı kullan (tool_call döndür).
Cevabını metin olarak uzun uzun yazmak yerine doğrudan aracı tetikle. Araçların açıklamalarını ve parametrelerini dikkatlice oku.

KURAL 3:
Dosya oluştururken, masaüstü veya belgeler gibi yerler söylenirse path parametresini "desktop" veya "documents" olarak belirt.

KURAL 4:
Eksik bilgi varsa veya mevcut araçlarla yapılamayacak bir şeyse durumu kullanıcıya açıkla.
"""


def test_native_tool_calling(user_message: str):
    print(f"\n--- TEST BAŞLIYOR: '{user_message}' ---")
    
    tools = get_tool_schemas()
    # Adım 1.3: tools=[] parametresi
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]

    try:
        client = ollama.Client(host='http://localhost:11434')
        response = client.chat(
            model=FAST_MODEL,
            messages=messages,
            tools=tools,
        )

        message = response.message
        
        # İç ses / Normal Yanıt
        if message.content:
            print(f"\n[Model Yanıtı / İç Ses]:\n{message.content.strip()}")
            
        # Tool Calls (Model bir araç çağırmaya karar verdiyse)
        if message.tool_calls:
            print("\n[Tool Call Yakalandı!]:")
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                args = tool_call.function.arguments
                print(f" -> Tetiklenen Araç: {function_name}")
                print(f" -> Parametreler: {args}")
                
                # İsteğe bağlı olarak yeteneği gerçekte çalıştırabiliriz (şimdilik sadece basıyoruz)
                # print(f" -> Simüle Çalıştırma Sonucu: {perform_skill(function_name, args)}")
        else:
            print("\n[Uyarı]: Model herhangi bir araç çağırmadı (Sadece metin döndü).")

    except Exception as exc:
        print(f"Hata: {exc}")


if __name__ == "__main__":
    # Test Senaryoları
    # 1. Dosya oluşturma isteği (file_skills)
    test_native_tool_calling("Masaüstüne proje adında yeni bir klasör oluştur.")
    
    # 2. Müzik çalma isteği (music_skills)
    test_native_tool_calling("Bana duman yürek çal.")
    
    # 3. İki aşamalı veya birden fazla sonuç gerektiren (Ollama modelinin kapasitesine bağlı)
    test_native_tool_calling("Google'da python nedir diye arat.")

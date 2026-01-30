from brain.intent_engine import process_command
from Skills.skills_manager import perform_skill

if __name__ == "__main__":
    print("------------------------------------------------")
    print("                  Jarvis")
    print("------------------------------------------------")

# --- HAFIZA LİSTESİ ---
    chat_history = [] 

    while True:
        user_input = input("\nSen: ")
        
        if user_input.lower() in ["çık", "exit"]:
            break
        if not user_input.strip():
            continue

        print("Jarvis düşünüyor...", end="\r")
        
        # 1. BEYİN: Analiz et (Artık geçmişi de gönderiyoruz)
        result = process_command(user_input, chat_history)
        
        # --- DEBUG (Görmek istersen açık kalsın) ---
        # print(f"\n[DEBUG] Gelen Veri: {result}") 

        print(" " * 20, end="\r")
        
        reply = result.get('reply', 'Efendim?')
        print(f"Jarvis: {reply}")
        
        action = result.get('action', 'unknown')
        parameters = result.get('parameters', {})
        
        # 2. KASLAR: İşlemi yap
        perform_skill(action, parameters)

        # --- HAFIZAYA KAYDET ---
        # 1. Senin dediğini kaydet
        chat_history.append({"role": "Kullanıcı", "content": user_input})
        
        # 2. Jarvis'in cevabını kaydet
        chat_history.append({"role": "Jarvis", "content": reply})
        
        # Hafıza şişmesin diye sadece son 10 mesajı tutalım
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]
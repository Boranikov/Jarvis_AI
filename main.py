from brain.intent_engine import process_command
from Skills.skills_manager import perform_skill

if __name__ == "__main__":
    print("------------------------------------------------")
    print("                  Jarvis")
    print("------------------------------------------------")

    while True:
        user_input = input("\nSen: ")
        
        if user_input.lower() in ["çık", "exit"]:
            break
        if not user_input.strip():
            continue

        print("Jarvis düşünüyor...", end="\r")
        
        # 1. Beyin (Analiz)
        result = process_command(user_input)
        
        print(" " * 20, end="\r")
        print(f"Jarvis: {result['reply']}")
        
        # 2. Kaslar (İşlem)
        # Artık 'data' yerine 'parameters' gönderiyoruz
        perform_skill(result['action'], result.get('parameters', {}))
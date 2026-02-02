"""
Jarvis AI Assistant - Ana Uygulama
Türkçe konuşan, yerel bir AI asistanı.
"""

from Brain.memory import Memory
from Core.handler import process_user_input, handle_presence_check
from Core.display import print_header
from Skills.skills_manager import perform_skill


def main():
    """Ana döngü"""
    print_header()
    memory = Memory()
    
    while True:
        user_input = input("Sen: ").strip()
        
        # Çıkış
        if user_input.lower() in ["çık", "exit", "quit"]:
            print("\nJarvis: Hoşça kalın efendim!")
            break
        
        # Boş girdi
        if not user_input:
            continue
        
        # Sistem kontrolü
        if handle_presence_check(user_input):
            continue
        
        # Bekleyen işlem kontrolü
        if memory.has_pending():
            result = memory.fill_pending(user_input)
            if result:
                action = result.get("action")
                params = result.get("params", {})
                print("Jarvis: İşleminiz tamamlanıyor efendim.")
                perform_skill(action, params)
                memory.clear_pending()
            else:
                print("Jarvis: Devam edebilirsiniz efendim.")
            continue
        
        # Normal işlem
        process_user_input(user_input, memory)


if __name__ == "__main__":
    main()

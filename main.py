"""
Jarvis AI Assistant - Ana Uygulama
Türkçe konuşan, yerel bir AI asistanı.
"""

from brain.intent_engine import process_command
from brain.memory import Memory
from Skills.skills_manager import perform_skill
from utils import extract_name_from_input
from config import (
    PRESENCE_TRIGGERS,
    REQUIRED_PARAMS,
    MISSING_QUESTIONS,
    ACTION_KEYWORDS,
    DEBUG_MODE
)


def print_header():
    """Başlık yazdır"""
    print("=" * 50)
    print("              JARVIS AI ASSISTANT")
    print("=" * 50)
    print("\nKullanıcı ile konuşmaya başlamak için yazın.")
    print("Çıkmak için 'çık' veya 'exit' yazın.\n")


def print_debug(action, params, path, name):
    """Debug bilgilerini yazdır"""
    if DEBUG_MODE:
        print(f"Debug: Action={action}, Params={params}, Path={path}, Name={name}")


def handle_presence_check(user_input: str) -> bool:
    """Sistem kontrolü yapılıyor mu kontrol et"""
    normalized = user_input.lower()
    if any(t in normalized for t in PRESENCE_TRIGGERS):
        print("Jarvis: Sizin için her zaman buradayım efendim.")
        return True
    return False


def process_user_input(user_input: str, memory: Memory):
    """Kullanıcı girdisini işle"""
    
    # Intent Engine'den sonuç al
    result = process_command(user_input, memory.get_history())
    
    action = result.get("action", "unknown")
    reply = result.get("reply", "Efendim?")
    params = result.get("parameters", {})
    path = result.get("path")
    name = result.get("name")
    
    # Yanıtı göster
    print(f"Jarvis: {reply}")
    print_debug(action, params, path, name)
    
    # === EKSİK PARAMETRE YÖNETİMİ ===
    if action == "missing_parameters":
        original_action = result.get("original_action")
        missing = params.get("missing", [])
        
        if original_action and missing:
            memory.set_pending(original_action, missing)
            question = MISSING_QUESTIONS.get(
                original_action, {}
            ).get(missing[0], "Devam edebilmem için bilgi verir misiniz efendim?")
            print(f"Jarvis: {question}")
        return
    
    # === ACTION'A GÖRE PARAMETRELERI AYARLA ===
    # Eğer intent engine'den name gelmemişse, user input'tan çıkar
    if not name and action in ACTION_KEYWORDS:
        extracted_name = extract_name_from_input(user_input, action)
        if extracted_name:
            name = extracted_name
    
    # Path ve name'i params'a ekle
    if path:
        params["path"] = path
    if name:
        params["name"] = name
    
    # === DOSYA/KLASÖR İŞLEMLERİ ===
    if action in ["create_file", "create_folder", "delete_file", "delete_folder"]:
        # Path varsayılanını belirle
        if not params.get("path"):
            params["path"] = "desktop"
        
        # Gerekli parametreleri kontrol et
        missing = [p for p in REQUIRED_PARAMS[action] if not params.get(p)]
        if missing:
            memory.set_pending(action, missing)
            question = MISSING_QUESTIONS[action][missing[0]]
            print(f"Jarvis: {question}")
            return
    
    # === DİĞER AKSIYONLAR ===
    elif action in REQUIRED_PARAMS:
        missing = [p for p in REQUIRED_PARAMS[action] if not params.get(p)]
        if missing:
            memory.set_pending(action, missing)
            question = MISSING_QUESTIONS[action][missing[0]]
            print(f"Jarvis: {question}")
            return
    
    # === SKILL ÇALIŞTIR ===
    if action not in ["small_talk", "unknown"]:
        perform_skill(action, params)
    
    # === HAFIZA'YA EKLE ===
    memory.add(user_input, reply)


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
            completed = memory.fill_pending(user_input)
            if completed:
                action, params = completed
                print("Jarvis: İşleminiz tamamlanıyor efendim.")
                perform_skill(action, params)
            else:
                print("Jarvis: Devam edebilirsiniz efendim.")
            continue
        
        # Normal işlem
        process_user_input(user_input, memory)


if __name__ == "__main__":
    main()


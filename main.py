"""
Jarvis AI Assistant - Ana Uygulama
Türkçe konuşan, yerel bir AI asistanı.
"""

from Brain.intent_engine import process_command
from Brain.memory import Memory
from Skills.skills_manager import perform_skill
from config import (
    PRESENCE_TRIGGERS,
    REQUIRED_PARAMS,
    MISSING_QUESTIONS,
    DEBUG_MODE
)


def print_header():
    """Başlık yazdır"""
    print("=" * 50)
    print("              JARVIS AI ASSISTANT")
    print("=" * 50)
    print("\nKullanıcı ile konuşmaya başlamak için yazın.")
    print("Çıkmak için 'çık' veya 'exit' yazın.\n")


def print_debug(action, path, name, parameters):
    """Debug bilgilerini yazdır"""
    if DEBUG_MODE:
        # Parameters'ı güvenli bir şekilde format et
        if isinstance(parameters, dict):
            params_str = str(parameters) if parameters else "{}"
        else:
            params_str = str(parameters)
        print(f"Debug: Action={action}, Path={path}, Name={name}, Params={params_str}")


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
    path = result.get("path")
    name = result.get("name")
    artist = result.get("artist")
    song = result.get("song")
    original_action = result.get("original_action")
    parameters = result.get("parameters", {})
    
    # Parameters'ın dict olmasını garantile
    if not isinstance(parameters, dict):
        parameters = {}
    
    # Yanıtı göster
    print(f"Jarvis: {reply}")
    print_debug(action, path, name, parameters)
    
    # === EKSİK PARAMETRE YÖNETİMİ ===
    if action == "missing_parameters":
        if original_action and parameters.get("missing"):
            # Orijinal parametreleri (path gibi) sakla
            original_params = {}
            if path:
                original_params["path"] = path
            if name:
                original_params["name"] = name
            if artist:
                original_params["artist"] = artist
            if song:
                original_params["song"] = song
            memory.set_pending(original_action, parameters.get("missing", []), original_params)
        return
    
    # === PARAMETRELERI DOLDUR ===
    if path:
        parameters["path"] = path
    if name:
        parameters["name"] = name
    if artist:
        parameters["artist"] = artist
    if song:
        parameters["song"] = song
    
    # Path varsayılanını belirle (dosya/klasör işlemleri için)
    if action in ["create_file", "create_folder", "delete_file", "delete_folder"]:
        if not parameters.get("path"):
            parameters["path"] = "desktop"
    
    # === SKILL ÇALIŞTIR ===
    if action not in ["small_talk", "unknown"]:
        perform_skill(action, parameters)
    
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


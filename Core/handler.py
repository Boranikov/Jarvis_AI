"""
Jarvis AI - Input Handler
Kullanıcı girdisi işleme fonksiyonları.
"""

from Brain.intent_engine import process_command
from Brain.memory import Memory
from Skills.skills_manager import perform_skill
from Core.display import print_debug
from config import PRESENCE_TRIGGERS


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
    song_name = result.get("song_name")
    original_action = result.get("original_action")
    parameters = result.get("parameters", {})
    
    # Parameters'ın dict olmasını garantile
    if not isinstance(parameters, dict):
        parameters = {}
    
    # Yanıtı göster
    print(f"Jarvis: {reply}")
    print_debug(action, path, name, parameters, song_name)
    
    # === EKSİK PARAMETRE YÖNETİMİ ===
    if action == "missing_parameters":
        if original_action and parameters.get("missing"):
            # Orijinal parametreleri (path gibi) sakla
            original_params = {}
            if path:
                original_params["path"] = path
            if name:
                original_params["name"] = name
            if song_name:
                original_params["song_name"] = song_name
            memory.set_pending(original_action, parameters.get("missing", []), original_params)
        return
    
    # === PARAMETRELERI DOLDUR ===
    if path:
        parameters["path"] = path
    if name:
        parameters["name"] = name
    if song_name:
        parameters["song_name"] = song_name
    
    # Path varsayılanını belirle (dosya/klasör işlemleri için)
    if action in ["create_file", "create_folder", "delete_file", "delete_folder"]:
        if not parameters.get("path"):
            parameters["path"] = "desktop"
    
    # === SKILL ÇALIŞTIR ===
    if action not in ["small_talk", "unknown"]:
        perform_skill(action, parameters)
    
    # === HAFIZA'YA EKLE ===
    memory.add(user_input, reply)

"""
Jarvis AI - Skills Manager
Skill yönlendirici - aksiyonları ilgili skill'lere yönlendirir.
"""

from Skills.file_skills import create_file, create_folder, delete_file, delete_folder
from Skills.music_skills import play_music
from Skills.web_skills import web_search


# Aksiyon -> Fonksiyon eşleştirmesi
SKILL_MAP = {
    "create_file": create_file,
    "create_folder": create_folder,
    "delete_file": delete_file,
    "delete_folder": delete_folder,
    "play_music": play_music,
    "web_search": web_search,
}


def perform_skill(action: str, params: dict) -> bool:
    """
    Belirtilen aksiyonu gerçekleştir.
    
    Args:
        action: Gerçekleştirilecek aksiyon
        params: Aksiyon parametreleri
        
    Returns:
        Başarılı ise True
    """
    # Params'ın dict olmasını garantile
    if not isinstance(params, dict):
        print(">> [ERROR] Parametreler hatalı format.")
        return False
    
    # Skill'i bul ve çalıştır
    skill_func = SKILL_MAP.get(action)
    
    if skill_func:
        return skill_func(params)
    else:
        print(f">> [WARNING] Bilinmeyen aksiyon: {action}")
        return False

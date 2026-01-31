"""
Jarvis AI Assistant - Konfigürasyon Dosyası
"""

# LLM Ayarları
LLM_MODEL = "gemma2:2b"
LLM_TEMPERATURE = 0.1

# Presence Triggers
PRESENCE_TRIGGERS = [
    "jarvis orda mısın",
    "jarvis orada mısın",
    "hey jarvis orda mısın",
    "hey jarvis orada mısın"
]

# Dikkat çekme kelimeleri
ATTENTION_WORDS = ["hey", "jarvis", "ey", "bre"]

# Action Keywords
ACTION_KEYWORDS = {
    "create_file": ["oluştur", "oluşturmak", "yap", "yapmak"],
    "create_folder": ["oluştur", "oluşturmak", "klasör", "folder"],
    "delete_file": ["sil", "silmek"],
    "delete_folder": ["sil", "silmek", "klasör", "folder"],
    "play_music": ["çal", "oyna", "spotify", "spotifydan", "müzik"],
    "web_search": ["ara", "aramak", "google", "ggle"]
}

# Gerekli parametreler
REQUIRED_PARAMS = {
    "create_file": ["name"],
    "create_folder": ["name"],
    "delete_file": ["name"],
    "delete_folder": ["name"]
}

# Eksik parametre soruları
MISSING_QUESTIONS = {
    "create_file": {
        "name": "Efendim, dosyanın ismini söyler misiniz?"
    },
    "create_folder": {
        "name": "Efendim, klasörün ismini söyler misiniz?"
    },
    "delete_file": {
        "name": "Efendim, silinecek dosyanın ismini belirtir misiniz?"
    },
    "delete_folder": {
        "name": "Efendim, silinecek klasörün ismini belirtir misiniz?"
    }
}

# Memory ayarları
MEMORY_HISTORY_LIMIT = 10

# Debug modu
DEBUG_MODE = True

"""
Jarvis AI Assistant - Konfigürasyon Dosyası
"""

# Model Ayarları
FAST_MODEL = "qwen2.5:3b"           # Hızlı komutlar için
REASONING_MODEL = "qwen2.5:7b"      # Düşünme/planlama için
LLM_TEMPERATURE = 0.1               # Hızlı model sıcaklığı
REASONING_TEMPERATURE = 0.3         # Reasoning model sıcaklığı

# Presence Triggers
PRESENCE_TRIGGERS = [
    "jarvis orda mısın",
    "jarvis orada mısın",
    "hey jarvis orda mısın",
    "hey jarvis orada mısın"
]

# Gerekli parametreler (referans olarak tutulmuştur)
REQUIRED_PARAMS = {
    "create_file": ["name", "path"],
    "create_folder": ["name", "path"],
    "delete_file": ["name", "path"],
    "delete_folder": ["name", "path"]
}

# Eksik parametre soruları (referans olarak tutulmuştur)
MISSING_QUESTIONS = {
    "create_file": {
        "name": "Dosyanın ismini söyler misiniz?"
    },
    "create_folder": {
        "name": "Klasörün ismini söyler misiniz?"
    },
    "delete_file": {
        "name": "Silinecek dosyanın ismini belirtir misiniz?"
    },
    "delete_folder": {
        "name": "Silinecek klasörün ismini belirtir misiniz?"
    }
}

# Memory ayarları
MEMORY_HISTORY_LIMIT = 10

# Debug modu
DEBUG_MODE = True

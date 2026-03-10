"""
Jarvis AI Assistant - Konfigürasyon Dosyası
"""

import logging
import sys
from types import MappingProxyType
from typing import FrozenSet

# Logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

def setup_logging(level: int = logging.DEBUG) -> logging.Logger:
    """Uygulama geneli logging yapılandırması."""
    root_logger = logging.getLogger("jarvis")
    
    if root_logger.handlers:
        return root_logger
    
    root_logger.setLevel(level)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    root_logger.addHandler(console_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Modül bazlı logger oluştur."""
    return logging.getLogger(f"jarvis.{name}")


# Model Ayarları
FAST_MODEL: str = "qwen3:1.7b"
REASONING_MODEL: str = "qwen2.5:7b"
CODING_MODEL: str = "qwen2.5-coder:14b"
LLM_TEMPERATURE: float = 0.1
REASONING_TEMPERATURE: float = 0.3

# Presence Triggers
PRESENCE_TRIGGERS: tuple[str, ...] = (
    "jarvis orda mısın",
    "jarvis orada mısın",
    "hey jarvis orda mısın",
    "hey jarvis orada mısın",
)

# Gerekli Parametreler
REQUIRED_PARAMS: MappingProxyType = MappingProxyType({
    "create_file": ("name",),
    "create_folder": ("name",),
    "delete_file": ("name",),
    "delete_folder": ("name",),
})

# Eksik Parametre Soruları
MISSING_QUESTIONS: MappingProxyType = MappingProxyType({
    "create_file": MappingProxyType({
        "name": "Dosyanın ismini söyler misiniz?",
    }),
    "create_folder": MappingProxyType({
        "name": "Klasörün ismini söyler misiniz?",
    }),
    "delete_file": MappingProxyType({
        "name": "Silinecek dosyanın ismini belirtir misiniz?",
    }),
    "delete_folder": MappingProxyType({
        "name": "Silinecek klasörün ismini belirtir misiniz?",
    }),
})

# Memory & Debug Ayarları
MEMORY_HISTORY_LIMIT: int = 10
DEBUG_MODE: bool = True

# Coding Engine Güvenlik Ayarları
MAX_TOOL_ITERATIONS: int = 15
MAX_FORMAT_RETRIES: int = 2
SAFETY_MODE: bool = False

# Çıkış Komutları
EXIT_COMMANDS: FrozenSet[str] = frozenset({"çık", "exit", "quit"})

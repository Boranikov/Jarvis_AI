"""
Jarvis AI Assistant - Yardımcı Fonksiyonlar
"""

def debug_print(message: str, data: dict = None):
    """Debug mesajı yazdır"""
    from config import DEBUG_MODE
    
    if DEBUG_MODE:
        print(f"Debug: {message}")
        if data:
            for key, value in data.items():
                print(f"  - {key}: {value}")

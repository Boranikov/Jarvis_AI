"""
Jarvis AI - Helper Utilities
Genel yardımcı fonksiyonlar.
"""

from Settings.config import DEBUG_MODE


def debug_print(message: str, data: dict = None):
    """Debug mesajı yazdır"""
    if DEBUG_MODE:
        print(f"Debug: {message}")
        if data:
            for key, value in data.items():
                print(f"  - {key}: {value}")


def clean_song_name(song_name: str) -> str:
    """
    Şarkı adından komut kelimelerini temizle.
    
    Args:
        song_name: Ham şarkı adı
        
    Returns:
        Temizlenmiş şarkı adı
    """
    if not song_name:
        return ""
    
    command_words = [
        "çal", "oynat", "aç", "dinle", "başlat",
        "spotify", "spotifydan", "spotify'dan", "müzik"
    ]
    
    words = song_name.lower().split()
    cleaned_words = [w for w in words if w not in command_words]
    return " ".join(cleaned_words).strip()

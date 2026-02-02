"""
Jarvis AI - Music Skills
Müzik çalma işlemleri.
"""

import webbrowser
import urllib.parse
from Utils.helpers import clean_song_name


def play_music(params: dict) -> bool:
    """
    Spotify'da müzik ara ve çal.
    
    Args:
        params: song_name içeren dictionary
        
    Returns:
        Başarılı ise True
    """
    song_name = params.get("song_name")
    
    if not song_name:
        print(">> [ERROR] Çalacak müzik belirtilmedi.")
        return False
    
    # Komut kelimelerini temizle
    cleaned_song_name = clean_song_name(song_name)
    
    if not cleaned_song_name:
        print(">> [ERROR] Çalacak müzik belirtilmedi.")
        return False
    
    try:
        encoded_song_name = urllib.parse.quote(cleaned_song_name)
        webbrowser.open(f"spotify:search:{encoded_song_name}")
        print(f">> [OK] Spotify'da '{cleaned_song_name}' aranıyor...")
        return True
    except Exception as e:
        print(f">> [ERROR] Spotify açma başarısız: {str(e)}")
        return False

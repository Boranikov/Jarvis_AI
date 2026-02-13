"""
Jarvis AI - Music Skills

Spotify API üzerinden müzik çalma işlemleri.
"""

import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from typing import Optional

from Utils.helpers import clean_song_name
from config import get_logger

logger = get_logger("skills.music")

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

_sp: Optional[spotipy.Spotify] = None


def _get_spotify() -> spotipy.Spotify:
    """Lazy Spotify client initialization."""
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=SPOTIPY_CLIENT_ID,
            client_secret=SPOTIPY_CLIENT_SECRET,
            redirect_uri=SPOTIPY_REDIRECT_URI,
            scope="user-modify-playback-state,user-read-playback-state",
        ))
    return _sp


def _get_active_device(sp: spotipy.Spotify) -> Optional[str]:
    """Aktif Spotify cihazını bul."""
    try:
        devices = sp.devices()
        if not devices or not devices.get("devices"):
            return None
        for device in devices["devices"]:
            if device.get("is_active"):
                return device["id"]
        return devices["devices"][0]["id"]
    except Exception as e:
        logger.error("Cihaz listesi alınamadı: %s", e)
        return None


def play_music(params: dict) -> bool:
    """
    Spotify'da müzik ara ve çal.

    Args:
        params: song_name içeren dictionary

    Returns:
        Başarılı ise True
    """
    song_name: str = clean_song_name(params.get("song_name", ""))
    if not song_name:
        logger.warning("Şarkı adı belirtilmedi")
        return False

    try:
        sp = _get_spotify()

        # 1. Şarkıyı ara
        sonuc = sp.search(q=song_name, limit=1, type="track")

        # 2. Sonuç var mı kontrol et
        if not sonuc or not sonuc["tracks"]["items"]:
            logger.warning("Spotify'da '%s' bulunamadı", song_name)
            return False

        # 3. İlk sonucu al
        track = sonuc["tracks"]["items"][0]
        track_id = track["id"]
        track_name = track["name"]
        artist_name = track["artists"][0]["name"]
        track_url = track["external_urls"].get("spotify", "")

        # 4. Aktif cihaz kontrolü
        device_id = _get_active_device(sp)

        if device_id:
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
            logger.info("Çalıyor: %s - %s", track_name, artist_name)
        else:
            # Cihaz yoksa web'de aç
            if track_url:
                webbrowser.open(track_url)
                logger.info("Cihaz bulunamadı, web'de açılıyor: %s - %s", track_name, artist_name)
            else:
                logger.warning("Cihaz ve URL bulunamadı: %s", song_name)
                return False

        return True

    except spotipy.exceptions.SpotifyException as e:
        logger.error("Spotify API hatası: %s", e)
        return False
    except Exception as e:
        logger.error("Müzik çalma hatası: %s", e)
        return False


def pause_music(params: dict = None) -> bool:
    """Çalan müziği duraklat."""
    try:
        sp = _get_spotify()
        sp.pause_playback()
        logger.info("Müzik duraklatıldı")
        return True
    except Exception as e:
        logger.error("Duraklama hatası: %s", e)
        return False

def resume_music(params: dict = None) -> bool:
    """Çalan müziği devam ettir."""
    try:
        sp = _get_spotify()
        sp.start_playback()
        logger.info("Müzik devam ediyor")
        return True
    except Exception as e:
        logger.error("Devam etme hatası: %s", e)
        return False


def get_current_track(params: dict = None) -> Optional[str]:
    """Şu an çalan şarkının bilgilerini formatlanmış string olarak döndür."""
    try:
        sp = _get_spotify()
        current = sp.current_playback()
        if not current or not current.get("item"):
            return None
        item = current["item"]
        track_name = item["name"]
        artist_name = item["artists"][0]["name"]
        return f"{track_name} - {artist_name}"
    except Exception as e:
        logger.error("Şu an çalan şarkı alınamadı: %s", e)
        return None
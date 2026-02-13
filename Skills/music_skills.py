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

import random

from Utils.helpers import clean_song_name
from config import get_logger

logger = get_logger("skills.music")

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

_sp: Optional[spotipy.Spotify] = None

# Duygu → Spotify genre/audio-feature mapping
# Üzgün kullanıcıya neşeli şarkılar, mutlu kullanıcıya enerjik şarkılar vb.
_EMOTION_MUSIC_MAP: dict[str, dict] = {
    "sad": {
        "genres": ["pop", "turkish pop", "chill"],
        "target_valence": 0.8,    # neşeli
        "target_energy": 0.7,     # enerjik
    },
    "negative": {
        "genres": ["pop", "turkish pop", "chill"],
        "target_valence": 0.8,
        "target_energy": 0.7,
    },
    "happy": {
        "genres": ["dance", "pop", "party"],
        "target_valence": 0.9,
        "target_energy": 0.85,
    },
    "positive": {
        "genres": ["dance", "pop", "party"],
        "target_valence": 0.9,
        "target_energy": 0.85,
    },
    "frustrated": {
        "genres": ["rock", "alternative", "metal"],
        "target_valence": 0.5,
        "target_energy": 0.9,
    },
    "angry": {
        "genres": ["rock", "metal", "hard-rock"],
        "target_valence": 0.4,
        "target_energy": 0.95,
    },
    "neutral": {
        "genres": ["indie", "acoustic", "chill"],
        "target_valence": 0.6,
        "target_energy": 0.5,
    },
    "curious": {
        "genres": ["indie", "jazz", "electronic"],
        "target_valence": 0.6,
        "target_energy": 0.5,
    },
}

# Varsayılan (bilinmeyen duygu)
_DEFAULT_EMOTION_CONFIG: dict = {
    "genres": ["pop", "chill"],
    "target_valence": 0.7,
    "target_energy": 0.6,
}


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


def _launch_spotify_and_wait(sp: spotipy.Spotify, timeout: int = 10) -> Optional[str]:
    """Spotify'ı başlat ve cihaz aktif olana kadar bekle."""
    try:
        os.startfile("spotify:")
        logger.info("Spotify başlatılıyor...")
        import time
        for i in range(timeout):
            time.sleep(1)
            device_id = _get_active_device(sp)
            if device_id:
                logger.info("Spotify cihazı bulundu (%d saniye)", i + 1)
                return device_id
        logger.warning("Spotify %d saniyede cihaz sağlayamadı", timeout)
        return None
    except Exception as e:
        logger.error("Spotify başlatma hatası: %s", e)
        return None


def _ensure_device(sp: spotipy.Spotify) -> Optional[str]:
    """Aktif cihaz bul, yoksa Spotify'ı başlat."""
    device_id = _get_active_device(sp)
    if device_id:
        return device_id
    return _launch_spotify_and_wait(sp)


def play_music(params: dict) -> bool:
    """
    Spotify'da müzik ara ve çal.

    Args:
        params: song_name veya emotion içeren dictionary

    Returns:
        Başarılı ise True
    """
    emotion: str = params.get("emotion", "")
    song_name: str = clean_song_name(params.get("song_name", ""))

    if not song_name and not emotion:
        logger.warning("Şarkı adı veya duygu belirtilmedi")
        return False

    try:
        sp = _get_spotify()

        # Duygu bazlı müzik: emotion varsa recommendations API kullan
        if emotion and not song_name:
            rec = _play_by_emotion(sp, emotion)
            if not rec:
                logger.warning("Duygu bazlı öneri bulunamadı, fallback...")
                return False

            track_id = rec["id"]
            track_name = rec["name"]
            artist_name = rec["artist"]
            track_url = rec["url"]
        else:
            # Normal şarkı arama
            sonuc = sp.search(q=song_name, limit=1, type="track")

            if not sonuc or not sonuc["tracks"]["items"]:
                logger.warning("Spotify'da '%s' bulunamadı", song_name)
                return False

            track = sonuc["tracks"]["items"][0]
            track_id = track["id"]
            track_name = track["name"]
            artist_name = track["artists"][0]["name"]
            track_url = track["external_urls"].get("spotify", "")

        # Cihaz bul ve çal
        device_id = _ensure_device(sp)

        if device_id:
            sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
            logger.info("Çalıyor: %s - %s", track_name, artist_name)
        elif track_url:
            webbrowser.open(track_url)
            logger.info("Cihaz bulunamadı, web'de açılıyor: %s - %s", track_name, artist_name)
        else:
            logger.warning("Spotify başlatılamadı ve URL bulunamadı")
            return False

        return True

    except spotipy.exceptions.SpotifyException as e:
        logger.error("Spotify API hatası: %s", e)
        return False
    except Exception as e:
        logger.error("Müzik çalma hatası: %s", e)
        return False

def _play_by_emotion(sp: spotipy.Spotify, emotion: str) -> Optional[dict]:
    """Duygu durumuna göre Spotify recommendations API ile şarkı bul."""
    config = _EMOTION_MUSIC_MAP.get(emotion.lower(), _DEFAULT_EMOTION_CONFIG)
    genres = config["genres"][:2]

    try:
        results = sp.recommendations(
            seed_genres=genres,
            target_valence=config["target_valence"],
            target_energy=config["target_energy"],
            limit=10,
        )

        tracks = results.get("tracks", [])
        if not tracks:
            logger.warning("Duygu '%s' için öneri bulunamadı", emotion)
            return None

        track = random.choice(tracks)
        return {
            "id": track["id"],
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "url": track["external_urls"].get("spotify", ""),
        }
    except Exception as e:
        logger.error("Recommendation API hatası: %s", e)
        return None


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

def next_track(params: dict = None) -> bool:
    """Çalan müziği değiştirir."""
    try:
        sp = _get_spotify()
        sp.next_track()
        logger.info("Müzik değiştirildi")
        return True
    except Exception as e:
        logger.error("Müzik değiştirme hatası: %s", e)
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
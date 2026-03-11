"""
Jarvis AI - Music Skills

Spotify API üzerinden müzik çalma işlemleri. 
Dependency Injection ve Clean Code prensiplerine uygun olarak MusicPlayer sınıfı ile sarmalanmıştır.
"""

import os
import random
import time
import threading
import webbrowser
import re
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

from Config.config import get_logger

logger = get_logger("skills.music")

_EMOTION_MUSIC_MAP: dict[str, dict] = {
    "negative": {
        "genres": ["pop", "turkish pop", "chill"],
        "target_valence": 0.8,
        "target_energy": 0.7,
    },
    "positive": {
        "genres": ["dance", "pop", "party"],
        "target_valence": 0.9,
        "target_energy": 0.85,
    },
    "neutral": {
        "genres": ["indie", "acoustic", "chill"],
        "target_valence": 0.6,
        "target_energy": 0.5,
    },
}

_DEFAULT_EMOTION_CONFIG: dict = {
    "genres": ["pop", "chill"],
    "target_valence": 0.7,
    "target_energy": 0.6,
}

def clean_music_query(text: str) -> str:
    """Gelen metinden 'çal', 'aç', 'oynat' gibi eylem kelimelerini temizler."""
    if not text:
        return ""
    # Eylem kelimelerini ve gereksiz boşlukları temizle
    patterns = [
        r"\bçal(armısın|armısın?|ar mısın|ar mısın?|sana|sın)?\b",
        r"\baç(armısın|ar mısın|sana|sın)?\b",
        r"\boynat\b",
        r"\bdüşün\b",
        r"\bbul(urmusun|ur musun|sana|sun)?\b",
        r"\bdinle(t|telim)?\b"
    ]
    cleaned = text.lower()
    for p in patterns:
        cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()


class MusicPlayer:
    """Spotify Yetenekleri Sınıfı (Dependency Injection için hazır)."""

    def __init__(self, sp: spotipy.Spotify) -> None:
        self.sp = sp

    def _get_active_device(self) -> Optional[str]:
        """Aktif Spotify cihazını bul."""
        try:
            devices = self.sp.devices()
            if not devices or not devices.get("devices"):
                return None
            for device in devices["devices"]:
                if device.get("is_active"):
                    return device["id"]
            return devices["devices"][0]["id"]
        except Exception as exc:
            logger.error("Cihaz listesi alınamadı: %s", exc)
            return None

    def _launch_spotify_async(self, timeout: int = 10) -> Optional[str]:
        """Spotify'ı başlat ve aktif cihazı non-blocking olarak bekle."""
        result_holder: dict = {"device_id": None}
        ready = threading.Event()

        def _poll() -> None:
            try:
                os.startfile("spotify:")
                time.sleep(2)
                for _ in range(int((timeout - 2) / 0.5)):
                    device_id = self._get_active_device()
                    if device_id:
                        result_holder["device_id"] = device_id
                        ready.set()
                        return
                    time.sleep(0.5)
            except Exception as exc:
                logger.error("Spotify başlatma hatası: %s", exc)
            ready.set()

        threading.Thread(target=_poll, daemon=True).start()
        ready.wait(timeout=timeout)
        return result_holder["device_id"]

    def _ensure_device(self) -> Optional[str]:
        """Aktif cihaz bul, yoksa Spotify'ı başlat."""
        return self._get_active_device() or self._launch_spotify_async()

    def _play_by_emotion(self, emotion: str) -> Optional[dict]:
        """Duygu durumuna göre Spotify Recommendations API ile şarkı bul."""
        config = _EMOTION_MUSIC_MAP.get(emotion.lower(), _DEFAULT_EMOTION_CONFIG)
        genres = config["genres"][:2]
        try:
            results = self.sp.recommendations(
                seed_genres=genres,
                target_valence=config["target_valence"],
                target_energy=config["target_energy"],
                limit=10,
            )
            tracks = results.get("tracks", [])
            if not tracks:
                return None
            track = random.choice(tracks)
            return {
                "id": track["id"],
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "url": track["external_urls"].get("spotify", ""),
            }
        except Exception as exc:
            logger.error("Recommendation API hatası: %s", exc)
            return None

    def play_music(self, song_name: Optional[str] = None, artist_name: Optional[str] = None, emotion: Optional[str] = None, query: Optional[str] = None) -> str:
        """Spotify'da müzik ara ve çal."""
        song_name = clean_music_query(song_name)
        artist_name = clean_music_query(artist_name)
        search_query = clean_music_query(query)
        
        # Eğer query varsa ama artist_name yoksa, query'yi artist_name olarak deneyebiliriz.
        if search_query and not artist_name and not song_name:
            artist_name = search_query

        if not song_name and not artist_name and not emotion:
            return "Şarkı adı, sanatçı veya duygu belirtilmedi."

        try:
            if emotion and not song_name:
                rec = self._play_by_emotion(emotion)
                if not rec:
                    return f"'{emotion}' duygusu için öneri bulunamadı."
                track_id = rec["id"]
                track_name = rec["name"]
                artist_name = rec["artist"]
                track_url = rec["url"]
            else:
                # Eğer song_name boş, ama artist_name varsa (örn: "Tarkan çal")
                if not song_name and artist_name:
                    logger.info(f"Spotify sanatçı sorgusu: {artist_name}")
                    sonuc = self.sp.search(q=artist_name, limit=1, type="artist")
                    
                    if sonuc and sonuc["artists"]["items"]:
                        artist = sonuc["artists"]["items"][0]
                        artist_name_found = artist["name"]
                        artist_uri = artist["uri"]
                        
                        device_id = self._ensure_device()
                        if device_id:
                            self.sp.start_playback(device_id=device_id, context_uri=artist_uri)
                            return f"SUCCESS: {artist_name_found} şarkılarını çalıyorum efendim."
                        elif artist["external_urls"].get("spotify"):
                            webbrowser.open(artist["external_urls"]["spotify"])
                            return f"SUCCESS (WEB): {artist_name_found} tarayıcıda açılıyor."
                        else:
                            return "Spotify cihazı bulunamadı ve URL alınamadı."
                    else:
                        return f"Spotify'da '{artist_name}' isimli sanatçı bulunamadı."
                
                # Hem song_name var hem de artist_name varsa klasik şarki arama
                query_str = ""
                if song_name and artist_name:
                    query_str = f"track:{song_name} artist:{artist_name}"
                elif song_name:
                    query_str = song_name
                
                logger.info(f"Spotify sorgusu: {query_str}")
                sonuc = self.sp.search(q=query_str, limit=1, type="track")
                
                if not sonuc or not sonuc["tracks"]["items"]:
                    # Eğer gelişmiş arama bulamazsa, basic fallback dene
                    fallback_query = f"{artist_name if artist_name else ''} {song_name if song_name else ''}".strip()
                    if fallback_query:
                        logger.info(f"Spotify fallback sorgusu: {fallback_query}")
                        sonuc = self.sp.search(q=fallback_query, limit=1, type="track")
                    
                if not sonuc or not sonuc["tracks"]["items"]:
                    return f"Spotify'da '{query_str}' için uygun bir sonuç bulunamadı."
                        
                track = sonuc["tracks"]["items"][0]
                track_id = track["id"]
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]
                track_url = track["external_urls"].get("spotify", "")

            device_id = self._ensure_device()

            if device_id:
                self.sp.start_playback(device_id=device_id, uris=[f"spotify:track:{track_id}"])
                return f"SUCCESS: {artist_name} grubundan {track_name} şarkısını çalıyorum efendim."
            elif track_url:
                webbrowser.open(track_url)
                return f"SUCCESS (WEB): Spotify uygulaması başlatılamadı ancak {artist_name} - {track_name} tarayıcıda açılıyor."
            else:
                return "Spotify cihazı bulunamadı ve URL alınamadı."

        except spotipy.exceptions.SpotifyException as exc:
            return f"Spotify API hatası: {str(exc)}"
        except Exception as exc:
            return f"Müzik çalma sırasında beklenmeyen hata oluştu: {str(exc)}"

    def pause_music(self) -> str:
        """Çalan müziği duraklat."""
        try:
            self.sp.pause_playback()
            return "Müzik duraklatıldı."
        except Exception as exc:
            return f"Müzik duraklatılırken hata oluştu: {str(exc)}"

    def resume_music(self) -> str:
        """Çalan müziği devam ettir."""
        try:
            self.sp.start_playback()
            return "Müzik devam ediyor."
        except Exception as exc:
            return f"Devam etme sırasında hata oluştu: {str(exc)}"

    def next_track(self) -> str:
        """Sıradaki şarkıya geç."""
        try:
            self.sp.next_track()
            return "Sonraki parçaya geçildi."
        except Exception as exc:
            return f"Sıradaki parçaya geçerken hata oluştu: {str(exc)}"

    def get_current_track(self) -> str:
        """Şu an çalan şarkının adını ve sanatçısını döndür."""
        try:
            current = self.sp.current_playback()
            if not current or not current.get("item"):
                return "Şu an çalan bir müzik bulunamadı."
            item = current["item"]
            return f"Şu an çalıyor: {item['name']} - {item['artists'][0]['name']}"
        except Exception as exc:
            return f"Çalan şarkı alınamadı: {str(exc)}"


# ==========================================
# Geriye Dönük Uyumluluk ve Instance Factory
# ==========================================

_player_instance: Optional[MusicPlayer] = None

def _get_player() -> MusicPlayer:
    global _player_instance
    if _player_instance is None:
        load_dotenv()
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                scope="user-modify-playback-state,user-read-playback-state",
            )
        )
        _player_instance = MusicPlayer(sp)
    return _player_instance

def play_specific_music(song_name: Optional[str] = None, artist_name: Optional[str] = None, query: Optional[str] = None) -> str:
    """Spotify'da müzik ara ve çal.
    
    song_name: Çalınacak şarkının SADECE adı (Örn: 'Yürek', 'Hello'). KESİNLİKLE 'çal', 'aç', 'dinlet' gibi eylem kelimeleri EKLEME. 
    artist_name: Şarkının sanatçısı (Örn: 'Duman', 'Adele'). Varsa MUTLAKA DOLDUR.
    query: Genel arama kelimesi.
    """
    return _get_player().play_music(song_name, artist_name, None, query)

def play_emotion_music(emotion: str) -> str:
    """Duygu durumuna göre Spotify'dan müzik çal.
    
    emotion: Çalınacak müziğin hissi/duygusu (öneri için).
    """
    return _get_player().play_music(None, None, emotion)

def pause_music() -> str:
    return _get_player().pause_music()

def resume_music() -> str:
    return _get_player().resume_music()

def next_track() -> str:
    return _get_player().next_track()

def get_current_track() -> str:
    return _get_player().get_current_track()
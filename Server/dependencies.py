"""
Jarvis AI — FastAPI Dependency Injection

SharedState: Uygulama ömrü boyunca paylaşılan kaynaklar.
SessionManager: Kullanıcı bazlı Memory instance havuzu (TTL ile otomatik temizlik).
"""

import time
from typing import Any

import httpx

from Brain.memory import Memory
from logging_config import get_logger
from settings import JarvisSettings, get_settings

logger = get_logger("server.dependencies")


class SessionManager:
    """
    Kullanıcı bazlı Memory instance havuzu.

    Her Telegram kullanıcısı kendi konuşma hafızasına sahiptir.
    TTL süresi dolan session'lar otomatik temizlenir.
    """

    def __init__(self, ttl_minutes: int = 60) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._ttl_seconds: int = ttl_minutes * 60

    def get_or_create(self, user_id: str) -> Memory:
        """
        Kullanıcıya ait Memory instance'ını döndür. Yoksa oluştur.

        Args:
            user_id: Kullanıcı tanımlayıcısı (örn: Telegram user ID)

        Returns:
            Kullanıcıya özel Memory instance
        """
        now = time.time()

        if user_id in self._sessions:
            session = self._sessions[user_id]
            session["last_access"] = now
            return session["memory"]

        memory = Memory()
        self._sessions[user_id] = {
            "memory": memory,
            "created_at": now,
            "last_access": now,
        }
        logger.info("session_created", user_id=user_id)
        return memory

    def cleanup_expired(self) -> int:
        """
        TTL süresi dolan session'ları temizle.

        Returns:
            Temizlenen session sayısı
        """
        now = time.time()
        expired = [
            uid
            for uid, session in self._sessions.items()
            if (now - session["last_access"]) > self._ttl_seconds
        ]
        for uid in expired:
            del self._sessions[uid]
            logger.info("session_expired", user_id=uid)
        return len(expired)

    @property
    def active_count(self) -> int:
        """Aktif session sayısı."""
        return len(self._sessions)


class SharedState:
    """
    Uygulama ömrü boyunca paylaşılan kaynaklar.
    FastAPI lifespan context manager tarafından yönetilir.
    """

    def __init__(self) -> None:
        self.settings: JarvisSettings = get_settings()
        self.session_manager: SessionManager = SessionManager(
            ttl_minutes=self.settings.session_ttl_minutes
        )
        self.http_client: httpx.AsyncClient | None = None
        self.start_time: float = time.time()

    async def startup(self) -> None:
        """Uygulama başlangıcında kaynakları başlat."""
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0),
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=10),
            follow_redirects=True,
        )
        logger.info(
            "shared_state_started",
            api_host=self.settings.api_host,
            api_port=self.settings.api_port,
        )

    async def shutdown(self) -> None:
        """Uygulama kapanışında kaynakları temizle."""
        if self.http_client:
            await self.http_client.aclose()
        logger.info("shared_state_shutdown")

    @property
    def uptime(self) -> float:
        """Sunucu çalışma süresi (saniye)."""
        return time.time() - self.start_time


# ── Singleton ──────────────────────────────────────────────
# FastAPI dependency injection için global instance.
# Lifespan tarafından başlatılır/kapatılır.

_shared_state: SharedState | None = None


def get_shared_state() -> SharedState:
    """Global SharedState instance'ını döndür."""
    global _shared_state
    if _shared_state is None:
        _shared_state = SharedState()
    return _shared_state


def set_shared_state(state: SharedState) -> None:
    """Global SharedState instance'ını ayarla (test için)."""
    global _shared_state
    _shared_state = state

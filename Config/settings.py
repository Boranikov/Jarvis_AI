"""
Jarvis AI — Tip-Güvenli Konfigürasyon (pydantic-settings)

Tüm ayarlar .env dosyasından veya ortam değişkenlerinden yüklenir.
Prefix: JARVIS_  (örn: JARVIS_API_PORT=8000)

Ağ: Cihazlar arası iletişim Tailscale mesh VPN üzerinden (100.x.x.x).
Mevcut config.py'ye DOKUNULMAZ — geriye uyumluluk korunur.
Bu dosya yalnızca dağıtık sistem (FastAPI, Qdrant, Nextcloud, n8n) için kullanılır.
"""

import os
import sys
from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_env_file() -> str:
    """EXE veya script dizinindeki .env dosyasının mutlak yolunu döndür."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, ".env")


class JarvisSettings(BaseSettings):
    """Dağıtık Jarvis sistemi için merkezi konfigürasyon."""

    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_prefix="JARVIS_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM Modelleri ──────────────────────────────────────
    fast_model: str = "qwen2.5:3b"
    reasoning_model: str = "qwen2.5:7b"
    coding_model: str = "qwen2.5-coder:14b"
    llm_temperature: float = 0.1
    reasoning_temperature: float = 0.3
    ollama_base_url: str = "http://localhost:11434"

    # ── API Sunucusu ───────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    cors_origins: list[str] = ["*"]

    # ── Uzak Sunucu (Ubuntu — Tailscale) ──────────────────
    remote_server_ip: str = "100.119.172.35"  # Ubuntu Tailscale IP

    # ── Qdrant (Vektörel Hafıza — Tailscale) ───────────
    qdrant_url: str = "http://100.119.172.35:6333"
    qdrant_collection: str = "jarvis_memory"
    qdrant_timeout: float = 10.0

    # ── Embedding ──────────────────────────────────────────
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int = 768

    # ── Nextcloud (Bulut Depolama — Tailscale) ─────────
    nextcloud_url: str = "http://100.119.172.35"
    nextcloud_user: str = "jarvis"
    nextcloud_pass: SecretStr = SecretStr("")
    nextcloud_webdav_path: str = "/remote.php/dav/files"

    # ── n8n (Otomasyon / Webhook — Tailscale) ────────
    n8n_webhook_url: str = "http://100.119.172.35:5678/webhook/jarvis-callback"
    n8n_timeout: float = 15.0

    # ── Hafıza ─────────────────────────────────────────────
    memory_history_limit: int = 10
    session_ttl_minutes: int = 60

    # ── Güvenlik ───────────────────────────────────────────
    max_tool_iterations: int = 15
    max_format_retries: int = 2
    safety_mode: bool = False

    # ── Debug ──────────────────────────────────────────────
    debug_mode: bool = True
    log_level: str = "DEBUG"
    log_format: str = "console"  # "console" veya "json"

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = v.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return upper

    @property
    def nextcloud_webdav_url(self) -> str:
        """Tam WebDAV URL'sini oluştur."""
        base = self.nextcloud_url.rstrip("/")
        path = self.nextcloud_webdav_path.rstrip("/")
        return f"{base}{path}/{self.nextcloud_user}"


@lru_cache(maxsize=1)
def get_settings() -> JarvisSettings:
    """Singleton settings instance döndür (cached)."""
    return JarvisSettings()

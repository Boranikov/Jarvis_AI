"""
Jarvis AI — API Request/Response Schemas

Pydantic v2 modelleri: n8n → FastAPI → Jarvis arasındaki veri kontratı.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Request Modelleri ──────────────────────────────────────


class ChatRequest(BaseModel):
    """n8n veya harici istemciden gelen sohbet isteği."""

    user_id: str = Field(
        ...,
        description="Kullanıcı tanımlayıcısı (örn: Telegram user ID)",
        examples=["123456789"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Kullanıcı mesajı",
        examples=["Merhaba Jarvis, bugün hava nasıl?"],
    )
    platform: Literal["telegram", "web", "cli", "api"] = Field(
        default="telegram",
        description="Mesajın geldiği platform",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Ek metadata (örn: Telegram chat_id, reply_to, vb.)",
    )


class WebhookCallbackRequest(BaseModel):
    """n8n'e geri gönderilecek callback verisi."""

    user_id: str
    message: str
    platform: str = "telegram"
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── Response Modelleri ─────────────────────────────────────


class ChatResponse(BaseModel):
    """Jarvis'in sohbet yanıtı."""

    response: str = Field(
        ...,
        description="Jarvis'in ürettiği yanıt metni",
    )
    session_id: str = Field(
        ...,
        description="Oturum tanımlayıcısı (kullanıcıya özel)",
    )
    action_taken: str | None = Field(
        default=None,
        description="Gerçekleştirilen aksiyon (varsa)",
        examples=["play_music", "create_file", None],
    )
    processing_time_ms: float = Field(
        ...,
        description="İşlem süresi (milisaniye)",
    )
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Yanıt zaman damgası",
    )


class HealthResponse(BaseModel):
    """Sistem sağlık durumu."""

    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ...,
        description="Genel sistem durumu",
    )
    uptime_seconds: float = Field(
        ...,
        description="Sunucu çalışma süresi (saniye)",
    )
    ollama_reachable: bool = Field(
        ...,
        description="Ollama LLM sunucusuna erişim durumu",
    )
    qdrant_reachable: bool = Field(
        ...,
        description="Qdrant vektör veritabanına erişim durumu",
    )
    version: str = Field(
        default="1.0.0",
        description="Jarvis API versiyonu",
    )


class ErrorResponse(BaseModel):
    """Standart hata yanıtı."""

    error: str = Field(..., description="Hata mesajı")
    detail: str | None = Field(default=None, description="Detaylı açıklama")
    request_id: str | None = Field(default=None, description="İstek takip ID'si")

"""
Jarvis AI — MCP Notification Tools

n8n webhook üzerinden Telegram ve diğer kanallara bildirim gönderme.
FastMCP @tool dekoratörü ile tanımlanır.
"""

from typing import Any

from MCP.tool_registry import mcp
from Config.logging_config import get_logger

logger = get_logger("mcp.tools.notification")

# n8n client referansı — uygulama başlangıcında set edilir
_n8n_client = None


def set_notification_client(client: Any) -> None:
    """N8NClient referansını ayarla (lifespan'da çağrılır)."""
    global _n8n_client
    _n8n_client = client


@mcp.tool()
async def send_telegram(
    user_id: str,
    message: str,
) -> str:
    """
    Telegram üzerinden kullanıcıya mesaj gönder.

    n8n otomasyon sistemi aracılığıyla Telegram Bot API'sine iletir.

    Args:
        user_id: Telegram kullanıcı ID'si
        message: Gönderilecek mesaj

    Returns:
        Başarı durumu mesajı
    """
    if _n8n_client is None:
        return "Bildirim sistemi bağlantısı kurulmamış."

    try:
        success = await _n8n_client.send_response(
            user_id=user_id,
            message=message,
            platform="telegram",
        )
        if success:
            return f"Mesaj Telegram'a gönderildi (user: {user_id})"
        return "Mesaj gönderilemedi."
    except Exception as exc:
        logger.error("send_telegram_error", user_id=user_id, error=str(exc))
        return f"Telegram gönderim hatası: {exc}"


@mcp.tool()
async def send_notification(
    event_type: str,
    title: str,
    body: str,
) -> str:
    """
    Genel bildirim gönder (alarm, hatırlatma, sistem bildirimi).

    Args:
        event_type: Bildirim tipi (alarm, reminder, system, info)
        title: Bildirim başlığı
        body: Bildirim içeriği

    Returns:
        Başarı durumu mesajı
    """
    if _n8n_client is None:
        return "Bildirim sistemi bağlantısı kurulmamış."

    try:
        success = await _n8n_client.notify(
            event_type=event_type,
            data={"title": title, "body": body},
        )
        if success:
            return f"Bildirim gönderildi: [{event_type}] {title}"
        return "Bildirim gönderilemedi."
    except Exception as exc:
        logger.error("notification_error", event_type=event_type, error=str(exc))
        return f"Bildirim hatası: {exc}"

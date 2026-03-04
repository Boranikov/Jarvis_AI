"""
Jarvis AI — n8n Webhook Callback Client

Jarvis'in cevabını n8n webhook'una POST ederek
Telegram'a (veya diğer kanallara) geri iletir.

Akış: Jarvis → n8n webhook → Telegram kullanıcısı
"""

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from logging_config import get_logger
from settings import JarvisSettings, get_settings

logger = get_logger("integrations.n8n")


class N8NClient:
    """
    n8n webhook callback client.

    Jarvis'in ürettiği yanıtları n8n otomasyon sunucusuna gönderir.
    n8n bu yanıtı Telegram Bot API üzerinden kullanıcıya iletir.

    Kullanım:
        client = N8NClient(settings)
        await client.send_response(
            user_id="123456789",
            message="Merhaba Efendim!",
            platform="telegram",
        )
    """

    def __init__(self, settings: JarvisSettings | None = None) -> None:
        self._settings = settings or get_settings()
        self._webhook_url = self._settings.n8n_webhook_url
        self._timeout = self._settings.n8n_timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy-initialized async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self._timeout, connect=5.0),
                follow_redirects=True,
            )
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def send_response(
        self,
        user_id: str,
        message: str,
        platform: str = "telegram",
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """
        Jarvis yanıtını n8n webhook'una POST et.

        n8n bu veriyi alıp Telegram Bot API üzerinden kullanıcıya iletir.

        Args:
            user_id: Hedef kullanıcı ID'si
            message: Gönderilecek mesaj
            platform: Hedef platform (telegram, web, vb.)
            metadata: Ek bilgiler (chat_id, reply_to_message_id, vb.)

        Returns:
            Başarı durumu
        """
        client = await self._get_client()

        payload: dict[str, Any] = {
            "user_id": user_id,
            "message": message,
            "platform": platform,
            "metadata": metadata or {},
        }

        try:
            response = await client.post(
                self._webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            success = response.status_code in (200, 201, 204)

            logger.info(
                "response_sent",
                user_id=user_id,
                platform=platform,
                status=response.status_code,
                success=success,
                message_length=len(message),
            )
            return success

        except httpx.ConnectError as exc:
            logger.error("n8n_connect_error", error=str(exc), url=self._webhook_url)
            raise
        except httpx.TimeoutException as exc:
            logger.error("n8n_timeout", error=str(exc), timeout=self._timeout)
            raise

    async def send_typing(self, user_id: str, platform: str = "telegram") -> None:
        """
        'Yazıyor...' bildirimi gönder (opsiyonel).

        Uzun işlemler sırasında kullanıcıya geri bildirim sağlar.

        Args:
            user_id: Hedef kullanıcı ID'si
            platform: Hedef platform
        """
        client = await self._get_client()

        try:
            await client.post(
                self._webhook_url,
                json={
                    "user_id": user_id,
                    "action": "typing",
                    "platform": platform,
                },
            )
        except Exception:
            # Typing bildirimi kritik değil, hatayı yut
            pass

    async def notify(
        self,
        event_type: str,
        data: dict[str, Any],
    ) -> bool:
        """
        Genel bildirim gönder (alarm, hatırlatma, vb.).

        Args:
            event_type: Olay tipi (alarm, reminder, system, vb.)
            data: Olay verileri

        Returns:
            Başarı durumu
        """
        client = await self._get_client()

        payload: dict[str, Any] = {
            "event_type": event_type,
            "data": data,
        }

        try:
            response = await client.post(
                self._webhook_url,
                json=payload,
            )

            success = response.status_code in (200, 201, 204)
            logger.info("notification_sent", event_type=event_type, success=success)
            return success

        except Exception as exc:
            logger.error("notification_error", event_type=event_type, error=str(exc))
            return False

    async def close(self) -> None:
        """HTTP client'ı kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("n8n_disconnected")

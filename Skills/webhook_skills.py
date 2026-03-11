import httpx
from Config.config import get_logger
from Config.settings import get_settings


logger = get_logger("skills.webhook")


def trigger_n8n_workflow(action_type: str, data: dict = None) -> str:
    """
    n8n otomasyon sunucusundaki webhook'u tetikleyerek harici işlemleri (e-posta gönderme, not oluşturma, takvim vb.) başlatır.
    
    Argümanlar:
        action_type: Yapılacak işlemin türü (örn: 'send_email', 'create_note', 'home_automation')
        data: İşlemle ilgili ek parametreler içeren sözlük (örn: {"to": "adres@mail.com", "subject": "Selam"})
    """
    settings = get_settings()
    url = settings.n8n_webhook_url

    if data is None:
        data = {}

    payload = {
        "action": action_type,
        "payload": data
    }
    logger.debug(f"n8n webhook tetikleniyor: {action_type} -> {url}")
    try:
        # 15 saniye zaman aşımı (timeout)
        response = httpx.post(url, json=payload, timeout=settings.n8n_timeout)
        response.raise_for_status()
        
        result_data = response.json()
        return f"n8n işlemi başarıyla tetiklendi. Yanıt: {result_data}"
        
    except httpx.HTTPStatusError as e:
        logger.error(f"n8n HTTP hatası: {e.response.status_code}")
        return f"İşlem başarısız oldu (HTTP {e.response.status_code})"
    except Exception as e:
        logger.error(f"n8n bağlantı hatası: {str(e)}")
        return f"n8n webhook bağlantı hatası: {str(e)}"
"""
Jarvis AI - Worker Thread

AI işlemlerini arka planda çalıştırır, UI donmaz.

Optimizasyonlar:
- Yeni unified process_input API'sını kullanır
- Type hints
- Spesifik exception handling
"""

from PyQt6.QtCore import QThread, pyqtSignal
import httpx
import json

from Brain.memory import Memory
from Config.config import get_logger
from Config.settings import get_settings

logger = get_logger("ui.worker")


class AIWorker(QThread):
    """AI işlemlerini arka planda HTTP üzerinden çalıştıran thread."""

    # Sinyal: İşlem tamamlandığında yanıtı gönder
    finished = pyqtSignal(str)

    def __init__(self, user_text: str, memory: Memory) -> None:
        super().__init__()
        self.user_text: str = user_text
        self.memory: Memory = memory

    def run(self) -> None:
        """Thread çalıştığında bu metot yürütülür."""
        try:
            settings = get_settings()
            # UI always hits the local Brain server
            api_url = f"http://127.0.0.1:{settings.api_port}/api/chat"
                
            logger.debug(f"AIWorker istek gönderiyor: {api_url}")

            # HTTP isteği gönder
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    api_url,
                    json={
                        "user_id": "gui_user",  # GUI için sabit veya dinamik alınabilir
                        "message": self.user_text,
                        "platform": "gui"
                    }
                )
                
            if response.status_code == 200:
                data = response.json()
                reply = data.get("response", "")
                self.finished.emit(reply)
            else:
                logger.error(f"Sunucu hatası: {response.status_code} - {response.text}")
                self.finished.emit(f"Sunucu bir hata döndürdü: HTTP {response.status_code}")

        except httpx.RequestError as exc:
            logger.error("AI Worker bağlantı hatası: %s", exc)
            self.finished.emit("Beyin sunucusuna (FastAPI) bağlanılamadı Efendim. Sunucunun açık olduğundan emin olun.")
        except Exception as exc:
            logger.error("AI Worker hatası: %s", exc, exc_info=True)
            self.finished.emit(f"Bir hata oluştu: {str(exc)}")

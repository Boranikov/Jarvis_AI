"""
Jarvis AI - Worker Thread

AI işlemlerini arka planda çalıştırır, UI donmaz.

Optimizasyonlar:
- Yeni unified process_input API'sını kullanır
- Type hints
- Spesifik exception handling
"""

from PyQt6.QtCore import QThread, pyqtSignal

from Brain.memory import Memory
from config import get_logger

logger = get_logger("ui.worker")


class AIWorker(QThread):
    """AI işlemlerini arka planda çalıştıran thread."""

    # Sinyal: İşlem tamamlandığında yanıtı gönder
    finished = pyqtSignal(str)

    def __init__(self, user_text: str, memory: Memory) -> None:
        super().__init__()
        self.user_text: str = user_text
        self.memory: Memory = memory

    def run(self) -> None:
        """Thread çalıştığında bu metot yürütülür."""
        try:
            # Import burada (circular import önlemek için)
            from Core.handler import process_input, OutputMode

            response: str = process_input(
                self.user_text, self.memory, OutputMode.GUI
            ) or ""
            self.finished.emit(response)
        except ConnectionError as exc:
            logger.error("AI Worker bağlantı hatası: %s", exc)
            self.finished.emit("Ollama bağlantısı kurulamadı Efendim.")
        except Exception as exc:
            logger.error("AI Worker hatası: %s", exc, exc_info=True)
            self.finished.emit(f"Bir hata oluştu: {str(exc)}")

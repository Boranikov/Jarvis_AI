"""
Jarvis AI - Memory Module

Konuşma geçmişini ve bekleyen işlemleri yönetir.
"""

<<<<<<< HEAD
from Settings.config import MEMORY_HISTORY_LIMIT
=======
from collections import deque
from typing import Optional

from Config.config import MEMORY_HISTORY_LIMIT, get_logger

logger = get_logger("brain.memory")
>>>>>>> 615e1f8a70867a991aa7761346541130f977e0f8


class Memory:
    """Konuşma hafızası yöneticisi."""

    def __init__(self) -> None:
        """Memory'yi başlangıç durumuna getir."""
        self.history: deque[dict[str, str]] = deque(maxlen=MEMORY_HISTORY_LIMIT)

    def add(self, user: str, jarvis: str) -> None:
        """
        Konuşmaya yeni bir girdi ekle.

        Args:
            user: Kullanıcı mesajı
            jarvis: Jarvis yanıtı
        """
        self.history.append({"user": user, "jarvis": jarvis})



    def get_history(self, limit: Optional[int] = None) -> list[dict[str, str]]:
        """
        Konuşma geçmişini döndür.

        Args:
            limit: Son kaç girdiyi döndüreceği (None = tümü)

        Returns:
            Konuşma geçmişi listesi
        """
        if limit:
            return list(self.history)[-limit:]
        return list(self.history)

    def clear_history(self) -> None:
        """Tüm konuşma geçmişini temizle."""
        self.history.clear()

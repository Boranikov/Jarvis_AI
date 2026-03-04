"""
Jarvis AI - Memory Module

Konuşma geçmişini ve bekleyen işlemleri yönetir.
"""

from collections import deque
from typing import Optional

from Config.config import MEMORY_HISTORY_LIMIT, get_logger

logger = get_logger("brain.memory")


class Memory:
    """Konuşma hafızası ve pending işlem yöneticisi."""

    def __init__(self) -> None:
        """Memory'yi başlangıç durumuna getir."""
        self.history: deque[dict[str, str]] = deque(maxlen=MEMORY_HISTORY_LIMIT)
        self.pending_action: Optional[str] = None
        self.pending_params: list[str] = []
        self.pending_values: dict[str, str] = {}
        self.original_params: dict[str, str] = {}

    def add(self, user: str, jarvis: str) -> None:
        """
        Konuşmaya yeni bir girdi ekle.

        Args:
            user: Kullanıcı mesajı
            jarvis: Jarvis yanıtı
        """
        self.history.append({"user": user, "jarvis": jarvis})

    def set_pending(
        self,
        action: str,
        params: list[str],
        original_params: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Bekleyen bir işlem ayarla (eksik parametreler).

        Args:
            action: Gerçekleştirilecek aksiyon
            params: Eksik parametreler listesi
            original_params: Zaten mevcut olan parametreler (ör: path)
        """
        self.pending_action = action
        self.pending_params = list(params)  # savunmacı kopya
        self.original_params = dict(original_params) if original_params else {}
        logger.debug("Pending set: action=%s, missing=%s", action, params)

    def has_pending(self) -> bool:
        """Bekleyen işlem var mı?"""
        return self.pending_action is not None

    def fill_pending(self, user_input: str) -> Optional[dict]:
        """
        Bekleyen işlemin parametresini doldur.
        Birden fazla parametre gerekiyorsa kullanıcıdan birer birer ister.

        Args:
            user_input: Kullanıcı girdisi (parametre değeri)

        Returns:
            {"action": str, "params": dict} tümü doldurulduysa, aksi halde None
        """
        if not self.pending_action or not self.pending_params:
            return None

        value: str = user_input.strip()
        param: str = self.pending_params.pop(0)
        self.pending_values[param] = value

        # Tüm parametreler doldurulduysa işlemi döndür
        if not self.pending_params:
            action: str = self.pending_action
            params: dict[str, str] = {**self.original_params, **self.pending_values}

            # Temizle
            self.pending_action = None
            self.pending_values = {}
            self.original_params = {}
            logger.debug("Pending completed: action=%s, params=%s", action, params)
            return {"action": action, "params": params}

        # Daha parametre lazım
        return None

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

    def clear_pending(self) -> None:
        """Bekleyen işlemi iptal et ve state'i sıfırla."""
        self.pending_action = None
        self.pending_params = []
        self.pending_values = {}
        self.original_params = {}

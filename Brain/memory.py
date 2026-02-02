"""
Jarvis Memory Module
Konuşma geçmişini ve bekleyen işlemleri yönet.
"""

from Settings.config import MEMORY_HISTORY_LIMIT


class Memory:
    """Konuşma hafızası ve pending işlemler"""
    
    def __init__(self):
        """Memory'yi başlat"""
        self.history = []
        self.pending_action = None
        self.pending_params = []

    def add(self, user: str, jarvis: str):
        """
        Konuşmaya yeni bir girdi ekle.
        
        Args:
            user: Kullanıcı mesajı
            jarvis: Jarvis yanıtı
        """
        self.history.append({"user": user, "jarvis": jarvis})
        if len(self.history) > MEMORY_HISTORY_LIMIT:
            self.history = self.history[-MEMORY_HISTORY_LIMIT:]

    def set_pending(self, action: str, params: list):
        """
        Bekleyen bir işlem ayarla (eksik parametreler).
        
        Args:
            action: Gerçekleştirilecek aksiyon
            params: Eksik parametreler listesi
        """
        self.pending_action = action
        self.pending_params = params.copy()

    def has_pending(self) -> bool:
        """Bekleyen işlem var mı?"""
        return self.pending_action is not None

    def fill_pending(self, user_input: str) -> tuple or None:
        """
        Bekleyen işlemin parametresini doldur.
        
        Args:
            user_input: Kullanıcı girdisi (parametre değeri)
            
        Returns:
            (action, params) tuple veya None
        """
        if not self.pending_action or not self.pending_params:
            return None

        value = user_input.strip()
        param = self.pending_params.pop(0)
        params = {param: value}

        # Tüm parametreler doldurulduysa, işlemi döndür
        if not self.pending_params:
            action = self.pending_action
            self.pending_action = None
            return action, params

        return None

    def get_history(self, limit: int = None) -> list:
        """
        Konuşma geçmişini döndür.
        
        Args:
            limit: Kaç tane son girdiyi istediğin
            
        Returns:
            Konuşma geçmişi
        """
        if limit:
            return self.history[-limit:]
        return self.history

    def clear_history(self):
        """Tüm geçmişi temizle"""
        self.history = []

    def clear_pending(self):
        """Bekleyen işlemi iptal et"""
        self.pending_action = None
        self.pending_params = []


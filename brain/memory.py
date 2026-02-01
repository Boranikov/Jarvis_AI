"""
Jarvis Memory Module
Konuşma geçmişini ve bekleyen işlemleri yönet.
"""

from config import MEMORY_HISTORY_LIMIT


class Memory:
    """Konuşma hafızası ve pending işlemler"""
    
    def __init__(self):
        """Memory'yi başlat"""
        self.history = []
        self.pending_action = None
        self.pending_params = []
        self.pending_values = {}
        self.original_params = {}

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

    def set_pending(self, action: str, params: list, original_params: dict = None):
        """
        Bekleyen bir işlem ayarla (eksik parametreler).
        
        Args:
            action: Gerçekleştirilecek aksiyon
            params: Eksik parametreler listesi
            original_params: Zaten mevcut olan parametreler (ör: path)
        """
        self.pending_action = action
        self.pending_params = params.copy()
        self.original_params = original_params.copy() if original_params else {}

    def has_pending(self) -> bool:
        """Bekleyen işlem var mı?"""
        return self.pending_action is not None

    def fill_pending(self, user_input: str):
        """
        Bekleyen işlemin parametresini doldur.
        Birden fazla parametre gerekiyorsa, kullanıcıdan birer birer ister.
        
        Args:
            user_input: Kullanıcı girdisi (parametre değeri)
            
        Returns:
            {"action": action, "params": params_dict} veya None
        """
        if not self.pending_action or not self.pending_params:
            return None

        value = user_input.strip()
        param = self.pending_params.pop(0)
        
        # Parametre değerini tutacak dict
        self.pending_values[param] = value

        # Tüm parametreler doldurulduysa, işlemi döndür
        if not self.pending_params:
            action = self.pending_action
            # Orijinal parametrelerle yeni parametreleri birleştir
            params = self.original_params.copy()
            params.update(self.pending_values)
            
            # Temizle
            self.pending_action = None
            self.pending_values = {}
            self.original_params = {}
            
            return {"action": action, "params": params}

        # Daha parametre lazım
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
        """Bekleyen işlemi iptal
        self.original_params = {} et"""
        self.pending_action = None
        self.pending_params = []
        self.pending_values = {}


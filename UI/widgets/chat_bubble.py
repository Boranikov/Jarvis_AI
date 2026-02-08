"""
Jarvis AI - Chat Bubble Widget
Mesaj balonları için özel widget.
"""

from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt


class ChatBubble(QWidget):
    """Sohbet mesaj balonu widget'ı"""
    
    def __init__(self, text: str, is_user: bool = False):
        super().__init__()
        self.is_user = is_user
        self.init_ui(text)
    
    def init_ui(self, text: str):
        """UI bileşenlerini oluştur"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Mesaj etiketi
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        if self.is_user:
            # Kullanıcı mesajı: Sağda
            self.label.setObjectName("userBubble")
            layout.addStretch()
            layout.addWidget(self.label)
        else:
            # Jarvis mesajı: Solda
            self.label.setObjectName("jarvisBubble")
            layout.addWidget(self.label)
            layout.addStretch()
        
        # Stil uygula
        # self.label.setStyleSheet(self._get_bubble_style()) -> Artık QSS'den alıyor
        
    def resizeEvent(self, event):
        """Widget yeniden boyutlandırıldığında"""
        # Balon genişliğini pencere genişliğinin %85'i ile sınırla
        if self.parent():
            max_width = int(self.parent().width() * 0.85)
            self.label.setMaximumWidth(max_width)
        super().resizeEvent(event)
    
    def set_text(self, text: str):
        """Mesaj metnini güncelle"""
        self.label.setText(text)

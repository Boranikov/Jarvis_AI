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
        self.label.setStyleSheet(self._get_bubble_style())
    
    def _get_bubble_style(self) -> str:
        """Balon stilini döndür"""
        if self.is_user:
            return """
                QLabel#userBubble {
                    background-color: #0f3460;
                    color: #eaeaea;
                    border-radius: 18px;
                    border-bottom-right-radius: 4px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-family: 'Segoe UI', sans-serif;
                }
            """
        else:
            return """
                QLabel#jarvisBubble {
                    background-color: #16213e;
                    color: #cdd6f4;
                    border-radius: 18px;
                    border-bottom-left-radius: 4px;
                    padding: 12px 16px;
                    font-size: 14px;
                    font-family: 'Segoe UI', sans-serif;
                    border: 1px solid #0f3460;
                }
            """
    
    def set_text(self, text: str):
        """Mesaj metnini güncelle"""
        self.label.setText(text)

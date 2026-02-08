"""
Jarvis AI - Ana Pencere (Main Window)
PyQt6 tabanlı modern sohbet arayüzü.
"""

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLineEdit, QPushButton, QLabel, QFrame,
    QApplication
)
from PyQt6.QtCore import Qt, QFile, QTextStream, QTimer
from PyQt6.QtGui import QFont

from UI.worker import AIWorker
from UI.widgets.chat_bubble import ChatBubble
from Brain.memory import Memory


class MainWindow(QMainWindow):
    """Jarvis AI Ana Penceresi"""
    
    def __init__(self):
        super().__init__()
        self.memory = Memory()
        self.worker = None
        self.thinking_bubble = None
        self.init_ui()
        self.load_styles()
    
    def init_ui(self):
        """Arayüz bileşenlerini oluştur"""
        self.setWindowTitle("Jarvis AI Assistant")
        self.setMinimumSize(500, 600)
        self.resize(650, 800)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # === HEADER ===
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(65)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 0, 15, 0)
        
        # Logo/Title
        title = QLabel("⚡ JARVIS")
        title.setObjectName("headerTitle")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Status
        self.status_label = QLabel("● Çevrimiçi")
        self.status_label.setObjectName("statusLabel")
        header_layout.addWidget(self.status_label)
        
        main_layout.addWidget(header)
        
        # === CHAT ALANI ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setObjectName("chatArea")
        
        self.chat_container = QWidget()
        self.chat_container.setObjectName("chatContainer")
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)
        
        # === INPUT ALANI ===
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_container.setFixedHeight(75)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(20, 12, 20, 12)
        input_layout.setSpacing(12)
        
        # Text input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Jarvis'e bir şey yaz...")
        self.input_field.setObjectName("inputField")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        # Send button
        self.send_button = QPushButton("Gönder")
        self.send_button.setObjectName("sendButton")
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        main_layout.addWidget(input_container)
        
        # Hoşgeldin mesajı
        self.add_message("Merhaba Efendim! Size nasıl yardımcı olabilirim?", is_user=False)
    
    def load_styles(self):
        """QSS stil dosyasını yükle"""
        # Stil dosyasının yolunu bul
        base_path = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(base_path, "styles.qss")
        
        style_file = QFile(style_path)
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
            style_file.close()
    
    def add_message(self, text: str, is_user: bool):
        """Sohbet alanına yeni mesaj ekle"""
        bubble = ChatBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        
        # Scroll'u en alta kaydır (küçük bir gecikmeyle)
        QTimer.singleShot(50, self._scroll_to_bottom)
    
    def _scroll_to_bottom(self):
        """Scroll alanını en alta kaydır"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def send_message(self):
        """Kullanıcı mesajını gönder ve AI yanıtını al"""
        user_text = self.input_field.text().strip()
        if not user_text:
            return
        
        # Çıkış komutu
        if user_text.lower() in ["çık", "exit", "quit"]:
            self.add_message(user_text, is_user=True)
            self.add_message("Hoşça kalın Efendim!", is_user=False)
            QTimer.singleShot(1500, self.close)
            return
        
        # Kullanıcı mesajını ekle
        self.add_message(user_text, is_user=True)
        self.input_field.clear()
        
        # Input'u devre dışı bırak
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        
        # Status güncelle
        self.status_label.setText("● Düşünüyor...")
        self.status_label.setStyleSheet("color: #f59e0b; font-size: 13px; padding-right: 10px;")
        
        # "Düşünüyor..." göstergesi
        self.thinking_bubble = ChatBubble("Düşünüyorum...", is_user=False)
        self.chat_layout.addWidget(self.thinking_bubble)
        self._scroll_to_bottom()
        
        # AI Worker'ı başlat (arayüz donmaz)
        self.worker = AIWorker(user_text, self.memory)
        self.worker.finished.connect(self.on_response_received)
        self.worker.start()
    
    def on_response_received(self, response: str):
        """AI yanıtı geldiğinde çağrılır"""
        # "Düşünüyorum" mesajını kaldır
        if self.thinking_bubble:
            self.thinking_bubble.deleteLater()
            self.thinking_bubble = None
        
        # Jarvis yanıtını ekle
        self.add_message(response, is_user=False)
        
        # Status'u geri al
        self.status_label.setText("● Çevrimiçi")
        self.status_label.setStyleSheet("color: #4ade80; font-size: 13px; padding-right: 10px;")
        
        # Input'u tekrar aktif et
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        event.accept()

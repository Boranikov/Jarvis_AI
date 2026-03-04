"""
Jarvis AI - Ana Pencere (Main Window)

PyQt6 tabanlı sohbet arayüzü.
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QLineEdit, QPushButton, QLabel, QFrame,
    QApplication,
)
from PyQt6.QtCore import Qt, QFile, QTextStream, QTimer
from PyQt6.QtGui import QFont

from UI.worker import AIWorker
from UI.widgets.chat_bubble import ChatBubble
from Brain.memory import Memory
from Config.config import EXIT_COMMANDS, get_logger

logger = get_logger("ui.main_window")


class MainWindow(QMainWindow):
    """Jarvis AI Ana Penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.memory: Memory = Memory()
        self.worker: Optional[AIWorker] = None
        self.thinking_bubble: Optional[ChatBubble] = None
        self.init_ui()
        self.load_styles()

    def init_ui(self) -> None:
        """Arayüz bileşenlerini oluştur."""
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

        title = QLabel("JARVIS")
        title.setObjectName("headerTitle")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.status_label = QLabel("● Çevrimiçi")
        self.status_label.setObjectName("statusLabel")
        header_layout.addWidget(self.status_label)

        main_layout.addWidget(header)

        # === CHAT ALANI ===
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
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

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Jarvis'e bir şey yaz...")
        self.input_field.setObjectName("inputField")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Gönder")
        self.send_button.setObjectName("sendButton")
        self.send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addWidget(input_container)

        # Hoşgeldin mesajı
        self.add_message("Merhaba Efendim! Size nasıl yardımcı olabilirim?", is_user=False)

    def load_styles(self) -> None:
        """QSS stil dosyasını yükle."""
        base_path: str = os.path.dirname(os.path.abspath(__file__))
        style_path: str = os.path.join(base_path, "styles.qss")

        style_file = QFile(style_path)
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
            style_file.close()
        else:
            logger.warning("Stil dosyası yüklenemedi: %s", style_path)

    def add_message(self, text: str, is_user: bool) -> None:
        """Sohbet alanına yeni mesaj ekle."""
        bubble = ChatBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self) -> None:
        """Scroll alanını en alta kaydır."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self) -> None:
        """Kullanıcı mesajını gönder ve AI yanıtını al."""
        user_text: str = self.input_field.text().strip()
        if not user_text:
            return

        # Çıkış komutu
        if user_text.lower() in EXIT_COMMANDS:
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
        self.status_label.setStyleSheet(
            "color: #ffffff; font-size: 13px; padding-right: 15px;"
        )

        # "Düşünüyor..." göstergesi
        self.thinking_bubble = ChatBubble("Düşünüyorum...", is_user=False)
        self.chat_layout.addWidget(self.thinking_bubble)
        self._scroll_to_bottom()

        # AI Worker'ı başlat
        self.worker = AIWorker(user_text, self.memory)
        self.worker.finished.connect(self.on_response_received)
        self.worker.start()

    def on_response_received(self, response: str) -> None:
        """AI yanıtı geldiğinde çağrılır."""
        if self.thinking_bubble:
            self.thinking_bubble.deleteLater()
            self.thinking_bubble = None

        self.add_message(response, is_user=False)

        self.status_label.setText("● Çevrimiçi")
        self.status_label.setStyleSheet(
            "color: #aaaaaa; font-size: 13px; padding-right: 15px;"
        )

        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

    def closeEvent(self, event) -> None:
        """Pencere kapatılırken worker'ı düzgün durdur."""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        event.accept()

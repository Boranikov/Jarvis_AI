"""
Jarvis AI — UI Launcher

Masaüstü ikonuna çift tıklayınca PyQt6 GUI'yi açar.
Arka plan sunucusu (JarvisServer.exe) zaten çalışıyor olmalıdır.
"""

import os
import sys

# ── Çalışma dizinini ayarla ───────────────────────────────
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)


def main() -> None:
    """PyQt6 GUI'yi başlat."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont, QIcon
    from UI.main_window import MainWindow

    app = QApplication(sys.argv)

    # Font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # İkon
    icon_path = os.path.join(BASE_DIR, "assets", "jarvis.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Pencere
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

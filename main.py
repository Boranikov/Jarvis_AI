"""
Jarvis AI Assistant - Ana Uygulama

Türkçe konuşan, yerel bir AI asistanı.
"""

import sys
import argparse

from config import EXIT_COMMANDS, setup_logging


def run_cli() -> None:
    """Konsol tabanlı arayüzü çalıştır."""
    from Brain.memory import Memory
    from Core.handler import process_input, handle_presence_check, OutputMode
    from Core.display import print_header
    from Skills.skills_manager import perform_skill

    print_header()
    memory = Memory()

    while True:
        try:
            user_input: str = input("Sen: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nJarvis: Hoşça kalın efendim!")
            break

        # Çıkış
        if user_input.lower() in EXIT_COMMANDS:
            print("\nJarvis: Hoşça kalın efendim!")
            break

        # Boş girdi
        if not user_input:
            continue

        # Sistem kontrolü
        if handle_presence_check(user_input):
            continue

        # Bekleyen işlem kontrolü
        if memory.has_pending():
            result = memory.fill_pending(user_input)
            if result:
                action: str = result.get("action", "")
                params: dict = result.get("params", {})
                print("Jarvis: İşleminiz tamamlanıyor efendim.")
                perform_skill(action, params)
                memory.clear_pending()
            else:
                print("Jarvis: Devam edebilirsiniz efendim.")
            continue

        # Ana işlem — unified API
        process_input(user_input, memory, OutputMode.CLI)


def run_gui() -> None:
    """Grafik arayüzü çalıştır."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QFont
    from UI.main_window import MainWindow

    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


def main() -> None:
    """Ana fonksiyon — GUI veya CLI modunu başlat."""
    # Logging altyapısını ilk iş olarak kur
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Jarvis AI Assistant - Türkçe konuşan yerel AI asistanı"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Konsol modunda çalıştır (varsayılan: GUI)",
    )
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()

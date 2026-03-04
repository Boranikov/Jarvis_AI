"""
Jarvis AI Assistant - Ana Uygulama

Türkçe konuşan, yerel bir AI asistanı.
Çalışma modları: --cli (konsol), --server (FastAPI), varsayılan (GUI)
"""

import sys
import argparse

from config import EXIT_COMMANDS, setup_logging


def run_cli() -> None:
    """Konsol tabanlı arayüzü çalıştır."""
    from Brain.memory import Memory
    from Core.handler import process_input, OutputMode
    from Core.display import print_header

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

        # Ana işlem — unified API (pending, presence, routing hepsi burada)
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


def run_server() -> None:
    """FastAPI sunucu modunu başlat (Dağıtık Jarvis — Beyin)."""
    import uvicorn
    from settings import get_settings

    settings = get_settings()

    print(f"🧠 Jarvis Brain başlatılıyor — {settings.api_host}:{settings.api_port}")
    print(f"📡 Ollama: {settings.ollama_base_url}")
    print(f"🗄️  Qdrant: {settings.qdrant_url}")
    print(f"📋 API Docs: http://localhost:{settings.api_port}/docs")

    uvicorn.run(
        "Server.app:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower(),
    )


def main() -> None:
    """Ana fonksiyon — GUI, CLI veya Server modunu başlat."""
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
    parser.add_argument(
        "--server",
        action="store_true",
        help="FastAPI sunucu modunda çalıştır (Dağıtık Jarvis)",
    )
    args = parser.parse_args()

    if args.server:
        run_server()
    elif args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()

"""
Jarvis AI Assistant - Ana Uygulama

Türkçe konuşan, yerel bir AI asistanı.
Çalışma modları: --cli (konsol), --server (FastAPI), varsayılan (GUI)
"""

import sys
import argparse

from Config.config import EXIT_COMMANDS, setup_logging


def run_cli() -> None:
    """Konsol tabanlı arayüzü çalıştır."""
    from Brain.memory import Memory
    from Core.handler import process_input, OutputMode
    from Core.display import print_header, console, print_jarvis_response
    import logging

    import asyncio

    print_header()
    memory = Memory()

    async def _cli_loop():
        while True:
            try:
                user_input: str = console.input("[bold #3B82F6]Sen:[/bold #3B82F6] ").strip()
            except (KeyboardInterrupt, EOFError):
                print_jarvis_response("Hoşça kalın efendim")
                break

            # Çıkış
            if user_input.lower() in EXIT_COMMANDS:
                print_jarvis_response("Hoşça kalın efendim")
                break

            # Boş girdi
            if not user_input:
                continue
                
            # Debug toggle
            if user_input.lower() == "/debug on":
                jarvis_logger = logging.getLogger("jarvis")
                jarvis_logger.setLevel(logging.DEBUG)
                for handler in jarvis_logger.handlers:
                    handler.setLevel(logging.DEBUG)
                logging.getLogger("httpx").setLevel(logging.DEBUG)
                print_jarvis_response("Debug modu AÇILDI. Arka plan işlemleri detaylı gösterilecek.")
                continue
            elif user_input.lower() == "/debug off":
                jarvis_logger = logging.getLogger("jarvis")
                jarvis_logger.setLevel(logging.WARNING)
                for handler in jarvis_logger.handlers:
                    handler.setLevel(logging.WARNING)
                logging.getLogger("httpx").setLevel(logging.WARNING)
                print_jarvis_response("Debug modu KAPATILDI. Sadece kritik hatalar gösterilecek.")
                continue

            # Ana işlem — unified API (pending, presence, routing hepsi burada)
            await process_input(user_input, memory, OutputMode.CLI)

    try:
        asyncio.run(_cli_loop())
    except KeyboardInterrupt:
        pass


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
    from Config.settings import get_settings

    settings = get_settings()

    print(f"[Jarvis Brain] Baslatiliyor — {settings.api_host}:{settings.api_port}")
    print(f"[Ollama] {settings.ollama_base_url}")
    print(f"[Qdrant] {settings.qdrant_url}")
    print(f"[API Docs] http://localhost:{settings.api_port}/docs")

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
    
    # FastMCP Toollarını sisteme kaydet
    from MCP.tool_registry import register_all_tools
    register_all_tools()
    
    # Dinamik Eklentileri (Plugins) belleğe entegre et
    from Core.plugin_loader import load_all_plugins
    load_all_plugins()

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

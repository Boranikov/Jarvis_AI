"""
Jarvis AI — System Tray Launcher

Arka planda sessizce çalışır:
  - System tray'de ikon gösterir
  - FastAPI sunucusunu background thread'de başlatır
  - İstek gelmediğinde CPU kullanmaz (~20MB RAM, %0 CPU)
  - Sağ tıkla menüsü: Docs, Health, Restart, Çıkış
"""

import os
import sys
import threading
import time
import webbrowser

import pystray
from PIL import Image, ImageDraw, ImageFont


# ── Çalışma dizinini ayarla ───────────────────────────────
# PyInstaller ile paketlendiğinde _MEIPASS altında çalışır
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)


# ── Tray İkonu Oluştur ────────────────────────────────────

def create_icon_image() -> Image.Image:
    """Programatik olarak Jarvis tray ikonu oluştur."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Arka plan: koyu mavi daire
    draw.ellipse([2, 2, size - 2, size - 2], fill=(20, 30, 60, 255))

    # İç halka: parlak mavi
    draw.ellipse([8, 8, size - 8, size - 8], outline=(0, 170, 255, 255), width=3)

    # Orta nokta: beyaz
    center = size // 2
    draw.ellipse(
        [center - 8, center - 8, center + 8, center + 8],
        fill=(0, 200, 255, 255),
    )

    # "J" harfi
    try:
        font = ImageFont.truetype("segoeui.ttf", 28)
    except OSError:
        font = ImageFont.load_default()

    draw.text((center - 8, center - 16), "J", fill=(255, 255, 255, 255), font=font)
    return img


# ── Sunucu Yönetimi ───────────────────────────────────────

class JarvisServer:
    """FastAPI sunucu yöneticisi — arka plan thread'inde çalışır."""

    def __init__(self):
        self._server = None
        self._thread = None
        self._running = False

    def start(self) -> None:
        """Sunucuyu başlat."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name="jarvis-server")
        self._thread.start()

    def _run(self) -> None:
        """Sunucu thread'i."""
        import uvicorn
        from settings import get_settings

        settings = get_settings()

        config = uvicorn.Config(
            "Server.app:app",
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower(),
            workers=1,
        )
        self._server = uvicorn.Server(config)
        self._server.run()
        self._running = False

    def stop(self) -> None:
        """Sunucuyu durdur."""
        if self._server:
            self._server.should_exit = True
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running


# ── Menü Aksiyonları ───────────────────────────────────────

server = JarvisServer()


def on_open_docs(icon, item) -> None:
    """Swagger docs'u tarayıcıda aç."""
    webbrowser.open("http://localhost:8000/docs")


def on_health(icon, item) -> None:
    """Health check sayfasını aç."""
    webbrowser.open("http://localhost:8000/api/health")


def on_restart(icon, item) -> None:
    """Sunucuyu yeniden başlat."""
    server.stop()
    time.sleep(1)
    server.start()
    icon.notify("Jarvis yeniden başlatıldı", "Jarvis AI")


def on_exit(icon, item) -> None:
    """Uygulamayı kapat."""
    server.stop()
    icon.stop()


def get_status_text(item) -> str:
    """Durum metnini döndür."""
    return f"Durum: {'Çalışıyor ✓' if server.is_running else 'Durdu ✗'}"


# ── Ana ────────────────────────────────────────────────────

def main() -> None:
    """System tray uygulamasını başlat."""
    # Sunucuyu arka planda başlat
    server.start()

    # Tray ikonu oluştur
    icon = pystray.Icon(
        name="Jarvis AI",
        icon=create_icon_image(),
        title="Jarvis AI Brain — Çalışıyor",
        menu=pystray.Menu(
            pystray.MenuItem(get_status_text, lambda icon, item: None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("API Docs", on_open_docs),
            pystray.MenuItem("Health Check", on_health),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Yeniden Baslat", on_restart),
            pystray.MenuItem("Cikis", on_exit),
        ),
    )

    # Başlangıç bildirimi
    icon.run_detached()
    time.sleep(0.5)
    icon.notify("Jarvis arka planda çalışıyor", "Jarvis AI")

    # Ana thread'i canlı tut
    try:
        while icon.visible:
            time.sleep(1)
    except KeyboardInterrupt:
        on_exit(icon, None)


if __name__ == "__main__":
    main()

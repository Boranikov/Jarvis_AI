"""
Jarvis AI — PyInstaller Build Script

Iki EXE olusturur:
  1. JarvisServer.exe — Arka plan sunucusu (system tray, konsol yok)
  2. JarvisUI.exe     — GUI arayuzu (cift tikla ac)

Kullanim:
    python build_exe.py
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "assets", "jarvis.ico")


def build_one(name: str, entry: str, console: bool = False) -> bool:
    """Tek bir EXE olustur."""

    data_args = [
        f"--add-data={os.path.join(BASE_DIR, '.env')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'config.py')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'settings.py')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'logging_config.py')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'assets')}{os.pathsep}assets",
    ]

    hidden_imports = [
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.websockets",
        "--hidden-import=uvicorn.protocols.websockets.auto",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=httptools",
        "--hidden-import=httptools.parser",
        "--hidden-import=httptools.parser.parser",
        "--hidden-import=dotenv",
        "--hidden-import=pystray._win32",
        "--hidden-import=ollama",
        "--hidden-import=httpx",
        "--hidden-import=qdrant_client",
        "--hidden-import=mcp",
        "--hidden-import=structlog",
        "--hidden-import=tenacity",
        "--hidden-import=pydantic_settings",
    ]

    collect_args = [
        "--collect-submodules=Server",
        "--collect-submodules=Core",
        "--collect-submodules=Brain",
        "--collect-submodules=Skills",
        "--collect-submodules=Integrations",
        "--collect-submodules=MCP",
        "--collect-submodules=Utils",
    ]

    # UI icin PyQt6 ekle
    if "ui" in name.lower():
        hidden_imports.append("--hidden-import=PyQt6")
        collect_args.append("--collect-submodules=UI")
        collect_args.append("--collect-submodules=PyQt6")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        f"--name={name}",
        "--noconsole" if not console else "--console",
        "--noconfirm",
        "--clean",
        f"--icon={ICON_PATH}",
        *data_args,
        *hidden_imports,
        *collect_args,
        os.path.join(BASE_DIR, entry),
    ]

    print(f"\n  Building {name}...")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    return result.returncode == 0


def build():
    print("=" * 50)
    print("  Jarvis AI - EXE Build")
    print("=" * 50)

    # 1. Server EXE (arka plan, konsol yok)
    ok1 = build_one("JarvisServer", "jarvis_tray.py", console=False)

    # 2. UI EXE (GUI, konsol yok)
    ok2 = build_one("JarvisUI", "jarvis_ui.py", console=False)

    print("\n" + "=" * 50)
    print("  SONUC")
    print("=" * 50)

    if ok1:
        server_exe = os.path.join(BASE_DIR, "dist", "JarvisServer", "JarvisServer.exe")
        size1 = os.path.getsize(server_exe) / (1024 * 1024) if os.path.exists(server_exe) else 0
        print(f"  [OK] JarvisServer.exe ({size1:.1f} MB)")
        print(f"       -> Arka plan sunucu, system tray")
        print(f"       -> shell:startup'a kisayol ekle")
    else:
        print(f"  [XX] JarvisServer.exe BUILD HATASI")

    if ok2:
        ui_exe = os.path.join(BASE_DIR, "dist", "JarvisUI", "JarvisUI.exe")
        size2 = os.path.getsize(ui_exe) / (1024 * 1024) if os.path.exists(ui_exe) else 0
        print(f"  [OK] JarvisUI.exe ({size2:.1f} MB)")
        print(f"       -> Masaustune kisayol olustur")
        print(f"       -> Cift tikla -> GUI acilir")
    else:
        print(f"  [XX] JarvisUI.exe BUILD HATASI")

    print("=" * 50)


if __name__ == "__main__":
    build()

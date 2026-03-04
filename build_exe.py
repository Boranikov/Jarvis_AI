"""
Jarvis AI — PyInstaller Build Script

Kullanım:
    python build_exe.py

Çıktı:
    dist/JarvisAI/JarvisAI.exe  (tek klasör — tüm bağımlılıklar dahil)
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def build():
    # Dahil edilecek veri dosyaları ve klasörler
    data_args = [
        f"--add-data={os.path.join(BASE_DIR, '.env')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'config.py')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'settings.py')}{os.pathsep}.",
        f"--add-data={os.path.join(BASE_DIR, 'logging_config.py')}{os.pathsep}.",
    ]

    # Dahil edilecek paketler (hidden imports)
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

    # Dahil edilecek proje modülleri
    collect_args = [
        "--collect-submodules=Server",
        "--collect-submodules=Core",
        "--collect-submodules=Brain",
        "--collect-submodules=Skills",
        "--collect-submodules=Integrations",
        "--collect-submodules=MCP",
        "--collect-submodules=Utils",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=JarvisAI",
        "--noconsole",              # Konsol penceresi gösterme (arka plan)
        "--noconfirm",              # Önceki build'i otomatik sil
        "--clean",                  # Cache temizle
        *data_args,
        *hidden_imports,
        *collect_args,
        os.path.join(BASE_DIR, "jarvis_tray.py"),
    ]

    print("=" * 50)
    print("  Jarvis AI — EXE Build Başlıyor")
    print("=" * 50)
    print(f"  Giriş:  jarvis_tray.py")
    print(f"  Çıkış:  dist/JarvisAI/JarvisAI.exe")
    print(f"  Mod:    --noconsole (arka plan)")
    print("=" * 50)

    result = subprocess.run(cmd, cwd=BASE_DIR)

    if result.returncode == 0:
        exe_path = os.path.join(BASE_DIR, "dist", "JarvisAI", "JarvisAI.exe")
        print()
        print("=" * 50)
        print(f"  BUILD BASARILI!")
        print(f"  EXE: {exe_path}")
        print(f"  Boyut: {os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        print("=" * 50)
        print()
        print("  Kullanim:")
        print("    1. dist/JarvisAI/JarvisAI.exe cift tikla")
        print("    2. System tray'de Jarvis ikonu belirir")
        print("    3. Sag tikla -> menu secenekleri")
        print()
        print("  Otomatik baslangic icin:")
        print("    Win+R -> shell:startup -> JarvisAI.exe kisayolunu buraya kopyala")
    else:
        print(f"\n  BUILD HATASI (exit code: {result.returncode})")
        sys.exit(1)


if __name__ == "__main__":
    build()

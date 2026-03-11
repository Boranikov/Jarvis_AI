"""
Jarvis AI — Dinamik Eklenti (Plugin) Yükleyici

Kullanıcıların .exe derlemesine (build) gerek kalmadan sisteme yeni yetenekler (FastMCP tools)
ekleyebilmesi için tasarlanmıştır. `Plugins/` klasöründeki Python scriptlerini
importlib kütüphanesi kullanarak çalışma zamanında (Runtime) dahil eder.
"""

import os
import sys
import importlib.util
from glob import glob

from Config.logging_config import get_logger

logger = get_logger("core.plugins")

# EXE için Base Dir'i bulma kalıbı (settings.py'dekiyle benzer)
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PLUGINS_DIR = os.path.join(BASE_DIR, "Plugins")

def _ensure_plugins_dir() -> None:
    """Plugins klasörü yoksa oluşturur ve örnek bir eklenti bırakır."""
    if not os.path.exists(PLUGINS_DIR):
        try:
            os.makedirs(PLUGINS_DIR)
            
            # Klasör yeni oluşturulduysa örnek bir script bırakalım
            sample_file = os.path.join(PLUGINS_DIR, "custom_greeting.py.example")
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write('"""Örnek Jarvis Eklentisidir. Aktif etmek için sonundaki .example uzantısını silin."""\n\n')
                f.write('from MCP.tool_registry import mcp\n\n')
                f.write('@mcp.tool()\n')
                f.write('def get_custom_greeting(name: str) -> str:\n')
                f.write('    """Kullanıcıya özel hissettiren bir karşılama metni döndürür."""\n')
                f.write('    return f"Merhaba {name}, eklenti sisteminiz harika çalışıyor!"\n')
                
            logger.info("Plugins klasörü başarıyla oluşturuldu.")
        except Exception as exc:
            logger.error(f"Plugins klasörü oluşturulamadı: {exc}")


def load_all_plugins() -> None:
    """
    Plugins/ dizinindeki tüm *.py dosyalarını bulur ve sisteme dahil eder.
    Dosyalar yüklendiğinde içlerindeki `@mcp.tool()` fonksiyonları otomatik olarak
    MCP registry defterine (tool_registry.py) kaydedilmiş olur.
    """
    _ensure_plugins_dir()

    # Plugins klasörünü path'e ekle (scriptlerin kendi içindeki importları için)
    if PLUGINS_DIR not in sys.path:
        sys.path.insert(0, PLUGINS_DIR)

    python_files = glob(os.path.join(PLUGINS_DIR, "*.py"))
    
    if not python_files:
        logger.debug("Plugins klasöründe yüklenecek aktif eklenti (Python dosyası) bulunamadı.")
        return

    loaded_count = 0
    for file_path in python_files:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # __init__.py gibi dosyaları atla
        if module_name.startswith("__"):
            continue

        try:
            # Dinamik Import Süreci (importlib)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Modülü sisteme kaydediyoruz ki double-import döngülerine girmesin
                sys.modules[module_name] = module
                # Kodu bellek üzerinde çalıştırıyoruz
                spec.loader.exec_module(module)
                loaded_count += 1
                logger.debug(f"Eklenti başarıyla yüklendi: {module_name}")
            else:
                logger.error(f"Eklenti okunurken Spec/Loader hatası: {module_name}")
        except Exception as exc:
             logger.error(f"Eklenti '{module_name}' yüklenirken hata oluştu: {exc}")

    if loaded_count > 0:
        logger.info(f"Toplam {loaded_count} eklenti başarıyla belleğe dahil edildi.")

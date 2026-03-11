"""
Jarvis AI - File Skills

Dosya ve klasör işlemleri. Tüm parametre doğrulaması Pydantic modelleri ile yapılır.
"""

import os
import shutil
from typing import Optional


from Utils.paths import get_path
from Config.config import get_logger

logger = get_logger("skills.file")


# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================

def _resolve_target(name: Optional[str], location: Optional[str], operation: str) -> Optional[str]:
    """ Paramterlerden tam yolu döndür """
    if not name and operation != "list_dir_recursive":
       logger.error("%s: name parametresi eksik", operation)
       return None
    
    if not location:
       logger.info("%s:konum belirtilemedi varsayılan olarak Masaüstü kullanılıyor", operation )
    
    base = get_path(location)
    return os.path.join(base,name) if name else base
    


# ==========================================
# YETENEK FONKSİYONLARI (SKILLS)
# ==========================================

def create_file(name: str, path: Optional[str] = None) -> bool:
    """Belirtilen konumda yeni bir dosya oluşturur. Uzantı yoksa .txt eklenir.
    
    name: Oluşturulacak dosyanın adı (Örn: 'notlar.txt').
    path: Dosyanın oluşturulacağı dizin (Örn: 'desktop', 'documents'). Boş bırakılırsa varsayılan yol kullanılır.
    """
    target = _resolve_target(name,path,"create_file")
    if not target:
       return False

    if "." not in os.path.basename(target):
       target += ".txt"

    try:
       os.makedirs(os.path.dirname(target), exist_ok=True)
       with open(target, "w", encoding="utf-8"):
           pass
       logger.info("Dosya oluşturuldu: %s", target)
       return True
    except (PermissionError, OSError) as exc:
       logger.error("Dosya oluşturma hatası: %s", exc)
       return False


def read_file(name: str, path: Optional[str] = None) -> str | bool:
    """Belirtilen dosyanın içeriğini okur ve string olarak geri döndürür.
    
    name: Okunacak dosyanın adı (Örn: 'notlar.txt').
    path: Dosyanın bulunduğu dizin (Örn: 'desktop').
    """
    target = _resolve_target(name, path, "read_file")
    if not target:
       return "HATA: Dosya yolu bulunamadı"

    try:
       with open(target, "r", encoding="utf-8") as fh:
           content = fh.read()
       logger.info("Dosya içeriği okundu: %s", target)
       return content
    except FileNotFoundError:
       logger.error("Dosya bulunamadı: %s", target)
       return False
    except (PermissionError, OSError) as exc:
       logger.error("Dosya okuma hatası: %s", exc)
       return False


def write_to_file(name: str, content: str, path: Optional[str] = None) -> bool:
    """Belirtilen dosyaya metin yazar. Dosya yoksa oluşturur, varsa üzerine yazar.
    
    name: Yazılacak dosyanın adı (Örn: 'hesap_makinesi.py').
    content: Dosya içine yazılacak içerik/kod.
    path: Dosyanın yazılacağı dizin (Örn: 'desktop/kodlar').
    """
    target = _resolve_target(name, path, "write_to_file")
    if not target:
       return False

    try:
       os.makedirs(os.path.dirname(target), exist_ok=True)
       with open(target, "w", encoding="utf-8") as fh:
           fh.write(content)
       logger.info("Dosyaya yazıldı: %s", target)
       return True
    except (PermissionError, OSError) as exc:
       logger.error("Dosyaya yazma hatası: %s", exc)
       return False


def list_dir_recursive(name: str, path: Optional[str] = None) -> str:
    """Belirtilen klasörün içinde bulunan dosyları ve klasörleri ağaç şeklinde listeler.
    
    name: Listelenecek klasörün adı.
    path: Klasörün bulunduğu üst dizin.
    """
    target = _resolve_target(name, path, "list_dir_recursive")

    if not target or not os.path.exists(target):
       return "HATA: Klasör bulunamadı."

    result: list[str] = []
    for root, _dirs, files in os.walk(target):
       level = root.replace(target, "").count(os.sep)
       indent = " " * 4 * level
       result.append(f"{indent}{os.path.basename(root)}/")
       subindent = " " * 4 * (level + 1)
       for f in files:
           result.append(f"{subindent}{f}")

    return "\n".join(result)


def create_folder(name: str, path: Optional[str] = None) -> bool:
    """Belirtilen yerde yeni bir klasör oluşturur.
    
    name: Oluşturulacak klasörün adı (Örn: 'yeni_proje').
    path: Klasörün oluşturulacağı üst dizin (Örn: 'desktop').
    """
    target = _resolve_target(name, path, "create_folder")
    if not target:
       return False

    try:
       os.makedirs(target, exist_ok=True)
       logger.info("Klasör oluşturuldu: %s", target)
       return True
    except (PermissionError, OSError) as exc:
       logger.error("Klasör oluşturma hatası: %s", exc)
       return False


def delete_file(name: str, path: Optional[str] = None) -> bool:
    """Belirtilen yerde bulunan dosyayı siler.
    
    name: Silinecek dosyanın adı.
    path: Dosyanın bulunduğu dizin.
    """
    target = _resolve_target(name, path, "delete_file")
    if not target:
       return False

    try:
       if os.path.exists(target):
           os.remove(target)
           logger.info("Dosya silindi: %s", target)
           return True
       logger.warning("Dosya bulunamadı: %s", target)
       return False
    except (PermissionError, OSError) as exc:
       logger.error("Dosya silme hatası: %s", exc)
       return False


def delete_folder(name: str, path: Optional[str] = None) -> bool:
    """Belirtilen klasörü içindekilerle beraber siler.
    
    name: Silinecek klasörün adı.
    path: Klasörün bulunduğu üst dizin.
    """
    target = _resolve_target(name,path, "delete_folder")
    if not target:
       return False

    try:
       if os.path.exists(target):
           shutil.rmtree(target)
           logger.info("Klasör silindi: %s", target)
           return True
       logger.warning("Klasör bulunamadı: %s", target)
       return False
    except (PermissionError, OSError) as exc:
       logger.error("Klasör silme hatası: %s", exc)
       return False

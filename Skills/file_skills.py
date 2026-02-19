"""
Jarvis AI - File Skills

Dosya ve klasör işlemleri.
"""

import os
import shutil
from typing import Optional

from Utils.paths import get_path
from config import get_logger

logger = get_logger("skills.file")


def _validate_params(params: dict, operation: str) -> Optional[str]:
    """Dosya/klasör parametrelerini doğrula ve hedef yolu döndür."""
    name: Optional[str] = params.get("name")
    if not name:
        logger.error("%s: İsim parametresi eksik", operation)
        return None

    location: Optional[str] = params.get("path")
    if not location:
        logger.info("%s: Konum belirtilmedi, varsayılan Desktop kullanılıyor", operation)
    return os.path.join(get_path(location), name)


def create_file(params: dict) -> bool:
    """
    Dosya oluştur.

    Args:
        params: name ve path içeren dictionary

    Returns:
        Başarılı ise True
    """
    target: Optional[str] = _validate_params(params, "create_file")
    if not target:
        return False

    # Uzantı yoksa .txt ekle
    if "." not in os.path.basename(target):
        target += ".txt"

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        # Context manager → exception durumunda otomatik kapatma
        with open(target, "w", encoding="utf-8"):
            pass
        logger.info("Dosya oluşturuldu: %s", target)
        return True
    except PermissionError as exc:
        logger.error("Dosya oluşturma izin hatası: %s", exc)
        return False
    except OSError as exc:
        logger.error("Dosya oluşturma başarısız: %s", exc)
        return False


def read_file(params: dict) -> str | bool:
    """
    Dosya oku.

    Args:
        params: {name: test.py, path: /home/boran/Desktop}

    Returns:
        Dosya içeriği (str) veya hata durumunda False
    """
    target: Optional[str] = _validate_params(params, "read_file")
    if not target:
        return "HATA: Dosya yolu bulunamadı"
    try:
        with open(target, "r", encoding="utf-8") as file:
            content = file.read()
            logger.info("Dosya içeriği okundu: %s", target)
            return content
    except FileNotFoundError:
        logger.error("Dosya bulunamadı: %s", target)
        return False
    except PermissionError as exc:
        logger.error("Dosya okuma izin hatası: %s", exc)
        return False
    except OSError as exc:
        logger.error("Dosya okuma başarısız: %s", exc)
        return False


def write_to_file(params: dict) -> bool:
    """
    Dosyaya yaz.

    Args:
        params: {name: test.py, path: /home/boran/Desktop, content: "Merhaba"}

    Returns:
        Başarılı ise True
    """
    target: Optional[str] = _validate_params(params, "write_to_file")
    if not target:
        return False
    
    content: Optional[str] = params.get("content")
    if content is None:
        logger.error("Dosyaya yazılamadı: İçerik parametresi eksik")
        return False
    
    try:
        # Dosya yoksa oluştur
        os.makedirs(os.path.dirname(target), exist_ok=True)
        # Dosyaya yaz
        with open(target, "w", encoding="utf-8") as file:
            file.write(content)
            logger.info("Dosyaya yazıldı: %s", target)
            return True
    except PermissionError as exc:
        logger.error("Dosyaya yazma izin hatası: %s", exc)
        return False
    except OSError as exc:
        logger.error("Dosyaya yazma başarısız: %s", exc)
        return False


def list_dir_recursive(params: dict) -> str:
    """
    Klasör altındaki dosya yapısını ağaç şeklinde listeler.
    Params: {"path": "..."} veya {"path": "desktop", "name": "proje"}

    Returns:
        Dosya ağacı string'i veya hata mesajı
    """
    # name opsiyonel, sadece path verilmiş olabilir
    if params.get("name"):
        target = _validate_params(params, "list_dir")
    else:
        target = get_path(params.get("path"))
    if not target or not os.path.exists(target):
         return "HATA: Klasör bulunamadı."
    result = []
    for root, dirs, files in os.walk(target):
        level = root.replace(target, '').count(os.sep)
        indent = ' ' * 4 * (level)
        result.append(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            result.append(f"{subindent}{f}")
            
    return "\n".join(result)



def create_folder(params: dict) -> bool:
    """
    Klasör oluştur.

    Args:
        params: name ve path içeren dictionary

    Returns:
        Başarılı ise True
    """
    target: Optional[str] = _validate_params(params, "create_folder")
    if not target:
        return False

    try:
        os.makedirs(target, exist_ok=True)
        logger.info("Klasör oluşturuldu: %s", target)
        return True
    except PermissionError as exc:
        logger.error("Klasör oluşturma izin hatası: %s", exc)
        return False
    except OSError as exc:
        logger.error("Klasör oluşturma başarısız: %s", exc)
        return False


def delete_file(params: dict) -> bool:
    """
    Dosya sil.

    Args:
        params: name ve path içeren dictionary

    Returns:
        Başarılı ise True
    """
    target: Optional[str] = _validate_params(params, "delete_file")
    if not target:
        return False

    try:
        if os.path.exists(target):
            os.remove(target)
            logger.info("Dosya silindi: %s", target)
            return True
        else:
            logger.warning("Dosya bulunamadı: %s", target)
            return False
    except PermissionError as exc:
        logger.error("Dosya silme izin hatası: %s", exc)
        return False
    except OSError as exc:
        logger.error("Dosya silme başarısız: %s", exc)
        return False


def delete_folder(params: dict) -> bool:
    """
    Klasör sil.

    Args:
        params: name ve path içeren dictionary

    Returns:
        Başarılı ise True
    """
    target: Optional[str] = _validate_params(params, "delete_folder")
    if not target:
        return False

    try:
        if os.path.exists(target):
            shutil.rmtree(target)
            logger.info("Klasör silindi: %s", target)
            return True
        else:
            logger.warning("Klasör bulunamadı: %s", target)
            return False
    except PermissionError as exc:
        logger.error("Klasör silme izin hatası: %s", exc)
        return False
    except OSError as exc:
        logger.error("Klasör silme başarısız: %s", exc)
        return False

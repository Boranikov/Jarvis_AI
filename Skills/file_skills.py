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

"""
Jarvis AI - File Skills

Dosya ve klasör işlemleri. Tüm parametre doğrulaması Pydantic modelleri ile yapılır.
"""

import os
import shutil
from typing import Optional

from pydantic import BaseModel, Field

from Utils.paths import get_path
from Config.config import get_logger

logger = get_logger("skills.file")


# ==========================================
# PYDANTIC MODELLERİ (LLM Şemaları İçin)
# ==========================================

class FileBaseParams(BaseModel):
    """Dosya/klasör adı ve konumu gerektiren temel işlemler için şema."""
    name: str = Field(
        ...,
        description="İşlem yapılacak dosya veya klasörün adı (örnek: test.txt, proje_klasoru).",
    )
    path: Optional[str] = Field(
        None,
        description=(
            "İşlem yapılacak konumun adı (örnek: desktop, documents, downloads). "
            "Belirtilmezse varsayılan olarak masaüstü (Desktop) kullanılır."
        ),
    )


class WriteFileParams(BaseModel):
    """Dosyaya yazmak için şema."""
    name: str = Field(..., description="Yazılacak dosyanın adı (örnek: main.py).")
    path: Optional[str] = Field(
        None,
        description="Dosyanın yazılacağı konum (örnek: desktop, C:/Proje). Belirtilmezse masaüstü kullanılır.",
    )
    content: str = Field(..., description="Dosyaya yazılacak tam metin içeriği.")


class ListDirParams(BaseModel):
    """Dizin listeleme için şema. name opsiyoneldir."""
    name: Optional[str] = Field(
        None,
        description="İçeriği listelenecek alt klasör adı. Belirtilmezse path konumunun kökü listelenir.",
    )
    path: Optional[str] = Field(
        None,
        description="Listelemenin yapılacağı ana konum (örnek: desktop, C:/Proje).",
    )


# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================

def _resolve_target(params: BaseModel, operation: str) -> Optional[str]:
    """Pydantic modelinden hedef tam yolu döndürür."""
    name: Optional[str] = getattr(params, "name", None)
    location: Optional[str] = getattr(params, "path", None)

    if not name and operation != "list_dir_recursive":
        logger.error("%s: name parametresi eksik", operation)
        return None

    if not location:
        logger.info("%s: Konum belirtilmedi, varsayılan Desktop kullanılıyor", operation)

    base = get_path(location)
    return os.path.join(base, name) if name else base


# ==========================================
# YETENEK FONKSİYONLARI (SKILLS)
# ==========================================

def create_file(params: FileBaseParams) -> bool:
    """Dosya oluştur. Uzantı yoksa .txt eklenir."""
    target = _resolve_target(params, "create_file")
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


def read_file(params: FileBaseParams) -> str | bool:
    """Dosya içeriğini oku ve string olarak döndür."""
    target = _resolve_target(params, "read_file")
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


def write_to_file(params: WriteFileParams) -> bool:
    """Dosyaya yaz (yoksa oluştur, varsa üzerine yaz)."""
    target = _resolve_target(params, "write_to_file")
    if not target:
        return False

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(params.content)
        logger.info("Dosyaya yazıldı: %s", target)
        return True
    except (PermissionError, OSError) as exc:
        logger.error("Dosyaya yazma hatası: %s", exc)
        return False


def list_dir_recursive(params: ListDirParams) -> str:
    """Klasör altındaki dosya yapısını ağaç şeklinde listeler."""
    target = _resolve_target(params, "list_dir_recursive")

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


def create_folder(params: FileBaseParams) -> bool:
    """Klasör oluştur."""
    target = _resolve_target(params, "create_folder")
    if not target:
        return False

    try:
        os.makedirs(target, exist_ok=True)
        logger.info("Klasör oluşturuldu: %s", target)
        return True
    except (PermissionError, OSError) as exc:
        logger.error("Klasör oluşturma hatası: %s", exc)
        return False


def delete_file(params: FileBaseParams) -> bool:
    """Dosya sil."""
    target = _resolve_target(params, "delete_file")
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


def delete_folder(params: FileBaseParams) -> bool:
    """Klasör sil (içindekilerle birlikte)."""
    target = _resolve_target(params, "delete_folder")
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

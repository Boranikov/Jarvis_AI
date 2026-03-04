"""
Jarvis AI - Path Utilities

Dosya yolu işlemleri.
"""

import os
from typing import Optional

from Config.config import get_logger

logger = get_logger("utils.paths")

# Modül seviyesinde bir kez hesapla (önceki: her get_path() çağrısında yeniden dict)
_USER_PROFILE: str = os.environ.get("USERPROFILE", os.path.expanduser("~"))

_LOCATION_MAP: dict[str, str] = {
    "desktop": os.path.join(_USER_PROFILE, "Desktop"),
    "documents": os.path.join(_USER_PROFILE, "Documents"),
    "downloads": os.path.join(_USER_PROFILE, "Downloads"),
    "music": os.path.join(_USER_PROFILE, "Music"),
    "pictures": os.path.join(_USER_PROFILE, "Pictures"),
}

_DEFAULT_LOCATION: str = _LOCATION_MAP["desktop"]


def get_path(location: Optional[str] = None) -> str:
    """
    Konum adından dosya yolunu döndür.

    Args:
        location: Konum adı (desktop, documents, vb.) veya
                  iç içe yol (desktop/klasor)

    Returns:
        Tam dosya yolu
    """
    if not location:
        return _DEFAULT_LOCATION

    # Path içinde "/" veya "\\" varsa → iç içe yol
    if "/" in location or "\\" in location:
        parts: list[str] = location.replace("\\", "/").split("/")
        base_key: str = parts[0].lower().strip()
        subpath: str = "/".join(parts[1:])

        resolved_base: str = _LOCATION_MAP.get(base_key, _DEFAULT_LOCATION)
        return os.path.join(resolved_base, subpath)

    # Basit konum
    return _LOCATION_MAP.get(location.lower().strip(), _DEFAULT_LOCATION)

"""
Jarvis AI - Path Utilities
Dosya yolu işlemleri.
"""

import os


def get_path(location: str) -> str:
    """
    Konum adından dosya yolunu döndür.
    
    Args:
        location: Konum adı (desktop, documents, vb.)
        
    Returns:
        Tam dosya yolu
    """
    base = os.environ["USERPROFILE"]
    locations = {
        "desktop": os.path.join(base, "Desktop"),
        "documents": os.path.join(base, "Documents"),
        "downloads": os.path.join(base, "Downloads"),
        "music": os.path.join(base, "Music"),
        "pictures": os.path.join(base, "Pictures")
    }
    return locations.get(location, os.path.join(base, "Desktop"))

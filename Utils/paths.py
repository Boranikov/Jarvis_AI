"""
Jarvis AI - Path Utilities
Dosya yolu işlemleri.
"""

import os


def get_path(location: str) -> str:
    """
    Konum adından dosya yolunu döndür.
    
    Args:
        location: Konum adı (desktop, documents, vb.) veya iç içe yol (desktop/klasor)
        
    Returns:
        Tam dosya yolu
    """
    if not location:
        location = "desktop"
    
    base = os.environ["USERPROFILE"]
    locations = {
        "desktop": os.path.join(base, "Desktop"),
        "documents": os.path.join(base, "Documents"),
        "downloads": os.path.join(base, "Downloads"),
        "music": os.path.join(base, "Music"),
        "pictures": os.path.join(base, "Pictures")
    }
    
    # Path içinde "/" veya "\" varsa -> iç içe yol
    if "/" in location or "\\" in location:
        # Normalize et
        parts = location.replace("\\", "/").split("/")
        base_location = parts[0].lower().strip()
        subpath = "/".join(parts[1:])
        
        # Base konumu çözümle
        resolved_base = locations.get(base_location, os.path.join(base, "Desktop"))
        
        # Alt klasörleri ekle
        return os.path.join(resolved_base, subpath)
    
    # Basit konum
    return locations.get(location.lower().strip(), os.path.join(base, "Desktop"))

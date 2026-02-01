"""
Jarvis Skills Manager
Tanımlanan aksiyonları gerçekleştir.
"""

import os
import webbrowser
import shutil


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


def perform_skill(action: str, params: dict):
    """
    Belirtilen aksiyonu gerçekleştir.
    
    Args:
        action: Gerçekleştirilecek aksiyon
        params: Aksiyon parametreleri
    """
    # Params'ın dict olmasını garantile
    if not isinstance(params, dict):
        print(">> [ERROR] Parametreler hatalı format.")
        return
    
    name = params.get("name")
    location = params.get("path")

    # Dosya/klasör işlemleri için name gerekli
    if action in ["create_file", "create_folder", "delete_file", "delete_folder"]:
        if not name:
            print(">> [ERROR] İsim olmadan işlem yapılamaz.")
            return
        
        target = os.path.join(get_path(location), name)

        # Dosya oluştur
        if action == "create_file":
            if "." not in name:
                target += ".txt"
            try:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                open(target, "w", encoding="utf-8").close()
                print(f">> [OK] Dosya oluşturuldu: {target}")
            except Exception as e:
                print(f">> [ERROR] Dosya oluşturma başarısız: {str(e)}")

        # Klasör oluştur
        elif action == "create_folder":
            try:
                os.makedirs(target, exist_ok=True)
                print(f">> [OK] Klasör oluşturuldu: {target}")
            except Exception as e:
                print(f">> [ERROR] Klasör oluşturma başarısız: {str(e)}")

        # Dosya sil
        elif action == "delete_file":
            try:
                if os.path.exists(target):
                    os.remove(target)
                    print(f">> [OK] Dosya silindi: {target}")
                else:
                    print(f">> [WARNING] Dosya bulunamadı: {target}")
            except Exception as e:
                print(f">> [ERROR] Dosya silme başarısız: {str(e)}")

        # Klasör sil
        elif action == "delete_folder":
            try:
                if os.path.exists(target):
                    shutil.rmtree(target)
                    print(f">> [OK] Klasör silindi: {target}")
                else:
                    print(f">> [WARNING] Klasör bulunamadı: {target}")
            except Exception as e:
                print(f">> [ERROR] Klasör silme başarısız: {str(e)}")

    # Müzik çal
    elif action == "play_music":
        if name:
            try:
                webbrowser.open(f"spotify:search:{name}")
                print(f">> [OK] Spotify'da '{name}' aranıyor...")
            except Exception as e:
                print(f">> [ERROR] Spotify açma başarısız: {str(e)}")
        else:
            print(">> [ERROR] Çalacak müzik belirtilmedi.")

    # Web araması yap
    elif action == "web_search":
        if name:
            try:
                webbrowser.open(f"https://www.google.com/search?q={name}")
                print(f">> [OK] Google'da '{name}' aranıyor...")
            except Exception as e:
                print(f">> [ERROR] Google açma başarısız: {str(e)}")
        else:
            print(">> [ERROR] Arama terimi belirtilmedi.")

    else:
        print(f">> [WARNING] Bilinmeyen aksiyon: {action}")


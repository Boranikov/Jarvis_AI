import os
import webbrowser
import shutil 

def get_path(location):
    base_path = os.environ['USERPROFILE'] 
    paths = {
        "desktop": os.path.join(base_path, "Desktop"),
        "documents": os.path.join(base_path, "Documents"),
        "downloads": os.path.join(base_path, "Downloads"),
        "music": os.path.join(base_path, "Music"),
        "pictures": os.path.join(base_path, "Pictures"),
    }
    return paths.get(location, paths["desktop"])

def perform_skill(action, params):
    if not isinstance(params, dict):
        params = {}

    name = params.get("name")
    location = params.get("location", "desktop")
    target_dir = get_path(location)
    
    # Tam yol oluşturma (Geçici)
    full_path = os.path.join(target_dir, name) if name else None

    # --- DOSYA OLUŞTURMA (GELİŞMİŞ) ---
    if action == "create_file":
        if name:
            # EĞER SONUNDA .txt YOKSA BİZ EKLEYELİM
            if "." not in name:
                name += ".txt"
                full_path = os.path.join(target_dir, name)
            
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write("") 
                print(f">> [Başarılı] Dosya oluşturuldu: {full_path}")
            except Exception as e:
                print(f">> [Hata] {e}")
        else:
            print(">> [Hata] Dosya ismi belirtilmedi.")

    # --- KLASÖR OLUŞTURMA ---
    elif action == "create_folder":
        if name:
            try:
                os.makedirs(full_path, exist_ok=True)
                print(f">> [Başarılı] Klasör oluşturuldu: {full_path}")
            except Exception as e:
                print(f">> [Hata] {e}")

    # --- KLASÖR SİLME (DİKKAT!) ---
    elif action == "delete_folder":
        if name and os.path.exists(full_path):
            try:
                # shutil.rmtree içi dolu klasörleri de siler
                shutil.rmtree(full_path)
                print(f">> [Silindi] Klasör temizlendi: {full_path}")
            except Exception as e:
                print(f">> [Hata] Silinemedi: {e}")
        else:
            print(f">> [Hata] Klasör bulunamadı: {full_path}")

    # --- DOSYA OLUŞTURMA ---
    elif action == "create_file":
        if name:
            try:
                # Boş bir dosya yaratır
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write("") 
                print(f">> [Başarılı] Dosya oluşturuldu: {full_path}")
            except Exception as e:
                print(f">> [Hata] {e}")

    # --- DOSYA SİLME ---
    elif action == "delete_file":
        if name and os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f">> [Silindi] Dosya yok edildi: {full_path}")
            except Exception as e:
                print(f">> [Hata] Silinemedi: {e}")
        else:
            print(f">> [Hata] Dosya bulunamadı.")

    # --- ESKİ YETENEKLER ---
    elif action == "play_music":
        print(f">> [Skill] Spotify açılıyor: {name}")
        webbrowser.open(f"spotify:search:{name}")

    elif action == "web_search":
        print(f">> [Skill] Google'da aranıyor: {name}")
        webbrowser.open(f"https://www.google.com/search?q={name}")
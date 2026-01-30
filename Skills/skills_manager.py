import os
import webbrowser
import shutil

def get_path(location):
    base = os.environ["USERPROFILE"]
    return {
        "desktop": os.path.join(base, "Desktop"),
        "documents": os.path.join(base, "Documents"),
        "downloads": os.path.join(base, "Downloads"),
        "music": os.path.join(base, "Music"),
        "pictures": os.path.join(base, "Pictures")
    }.get(location, os.path.join(base, "Desktop"))

def perform_skill(action, params):
    name = params.get("name")
    location = params.get("location", "desktop")

    if not name:
        print(">> [Hata] İsim olmadan işlem yapılamaz.")
        return

    target = os.path.join(get_path(location), name)

    if action == "create_file":
        if "." not in name:
            target += ".txt"
        open(target, "w", encoding="utf-8").close()
        print(f">> [OK] Dosya oluşturuldu: {target}")

    elif action == "create_folder":
        os.makedirs(target, exist_ok=True)
        print(f">> [OK] Klasör oluşturuldu: {target}")

    elif action == "delete_file" and os.path.exists(target):
        os.remove(target)
        print(f">> [Silindi] {target}")

    elif action == "delete_folder" and os.path.exists(target):
        shutil.rmtree(target)
        print(f">> [Silindi] {target}")

    elif action == "play_music":
        webbrowser.open(f"spotify:search:{name}")

    elif action == "web_search":
        webbrowser.open(f"https://www.google.com/search?q={name}")

"""
Jarvis AI - Display Functions
Kullanıcı arayüzü ve çıktı fonksiyonları.
"""

from config import DEBUG_MODE


def print_header():
    """Başlık yazdır"""
    print("=" * 50)
    print("              JARVIS AI ASSISTANT")
    print("=" * 50)
    print("\nKullanıcı ile konuşmaya başlamak için yazın.")
    print("Çıkmak için 'çık' veya 'exit' yazın.\n")


def print_debug(action, path, name, parameters, song_name):
    """Debug bilgilerini yazdır"""
    if DEBUG_MODE:
        # Parameters'ı güvenli bir şekilde format et
        if isinstance(parameters, dict):
            params_str = str(parameters) if parameters else "{}"
        else:
            params_str = str(parameters)
        print(f"Debug: Action={action}, Path={path}, Name={name}, Params={params_str}")
        if action == "play_music":
            print(f"Debug: Song Name={song_name}")

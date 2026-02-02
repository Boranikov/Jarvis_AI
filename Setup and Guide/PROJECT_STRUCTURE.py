"""
Jarvis AI Assistant - Proje Yapısı Özeti
"""

PROJECT_STRUCTURE = """
Jarvis_Aİ/
│
├── main.py                    # Ana uygulama - entry point
├── config.py                  # Konfigürasyon dosyası
├── setup.py                   # Kurulum betiği
├── requirements.txt           # Python bağımlılıkları
├── README.md                  # Proje dokümantasyonu
├── .gitignore                 # Git ignore kuralları
│
├── Core/                      # Ana işleme modülü
│   ├── __init__.py
│   ├── handler.py             # Kullanıcı girdisi işleme
│   │   ├── process_user_input()    # Input -> Intent -> Skill
│   │   └── handle_presence_check() # "Jarvis orda mısın?" kontrolü
│   └── display.py             # UI ve çıktı fonksiyonları
│       ├── print_header()     # Başlık yazdır
│       └── print_debug()      # Debug bilgileri
│
├── Brain/                     # NLP ve Intent Engine modülü
│   ├── __init__.py
│   ├── intent_engine.py       # LLM tabanlı intent tanıma
│   │   └── process_command()  # User input -> JSON (action, params)
│   └── memory.py              # Konuşma hafızası ve state yönetimi
│       └── Memory class       # History ve pending işlemler
│
├── Skills/                    # Beceri modülleri
│   ├── __init__.py
│   ├── skills_manager.py      # Skill yönlendirici (router)
│   │   └── perform_skill()    # Action'ı ilgili skill'e yönlendir
│   ├── file_skills.py         # Dosya/klasör işlemleri
│   │   ├── create_file()
│   │   ├── create_folder()
│   │   ├── delete_file()
│   │   └── delete_folder()
│   ├── music_skills.py        # Müzik çalma
│   │   └── play_music()       # Spotify'da arama
│   └── web_skills.py          # Web araması
│       └── web_search()       # Google'da arama
│
└── Utils/                     # Yardımcı fonksiyonlar
    ├── __init__.py
    ├── paths.py               # Path işlemleri
    │   └── get_path()         # "desktop" -> C:/Users/.../Desktop
    └── helpers.py             # Genel yardımcılar
        ├── clean_song_name()  # Komut kelimelerini temizle
        └── debug_print()      # Debug mesajı yazdır
"""

MODULE_DESCRIPTIONS = {
    "main.py": "Sadece entry point ve ana döngü (50 satır)",
    
    "config.py": "Tüm konfigürasyon ayarları (LLM, triggers, vb.)",
    
    "Core/handler.py": """
    - Kullanıcı girdisini işler
    - Intent Engine'i çağırır
    - Skill'leri tetikler
    - Eksik parametre yönetimi
    """,
    
    "Core/display.py": """
    - UI fonksiyonları (header, debug)
    - Çıktı formatlama
    """,
    
    "Brain/intent_engine.py": """
    - Ollama LLM'i kullanarak user input'ı analiz eder
    - JSON formatında action ve parametreleri çıkarır
    - System prompt ile modeli yönlendirir
    """,
    
    "Brain/memory.py": """
    - Konuşma geçmişini tutar (son 10 konuşma)
    - Bekleyen işlemleri (pending actions) yönetir
    - State ve session yönetimi
    """,
    
    "Skills/skills_manager.py": """
    - Sadece router görevi görür
    - Action'ı ilgili skill fonksiyonuna yönlendirir
    - SKILL_MAP ile aksiyon-fonksiyon eşleştirmesi
    """,
    
    "Skills/file_skills.py": """
    - Dosya oluşturma/silme
    - Klasör oluşturma/silme
    """,
    
    "Skills/music_skills.py": """
    - Spotify'da müzik arama ve çalma
    - Komut kelimelerini temizleme
    """,
    
    "Skills/web_skills.py": """
    - Google'da web araması
    """,
    
    "Utils/paths.py": """
    - Konum adından dosya yolu dönüşümü
    - desktop, documents, downloads, vb.
    """,
    
    "Utils/helpers.py": """
    - clean_song_name(): Şarkı adından komut kelimelerini çıkar
    - debug_print(): Debug mesajları
    """,
}

FEATURES = {
    "✓ Modüler Yapı": "Her özellik ayrı dosyada",
    "✓ NLP Intent Recognition": "Ollama LLM ile intent tanıma",
    "✓ Dosya Yönetimi": "Dosya ve klasör oluştur/sil",
    "✓ Spotify Entegrasyonu": "Spotify'da müzik ara ve çal",
    "✓ Web Arama": "Google'da ara",
    "✓ Konuşma Hafızası": "Son 10 konuşmayı hatırla",
    "✓ Multi-step Actions": "Eksik parametreler için sorgu",
    "✓ Error Handling": "Kapsamlı hata yönetimi",
}

USAGE_EXAMPLES = {
    "Dosya Oluşturma": [
        "jarvis, test.txt oluştur",
        "masaüstüne deneme dosyası oluştur",
    ],
    
    "Klasör Oluşturma": [
        "jarvis, yeni klasör oluştur",
        "my_folder klasörü oluştur",
    ],
    
    "Müzik Çalma": [
        "jarvis, tarkan dudu dudu çal",
        "sezen aksu tükeneceğiz çal",
    ],
    
    "Web Arama": [
        "jarvis, python ara",
        "google'da AI ara",
    ],
}


def print_structure():
    """Proje yapısını göster"""
    print(PROJECT_STRUCTURE)
    print("\n" + "=" * 60)
    print("MODÜL AÇIKLAMALARI")
    print("=" * 60)
    for module, desc in MODULE_DESCRIPTIONS.items():
        print(f"\n📄 {module}")
        print(f"   {desc}")
    
    print("\n" + "=" * 60)
    print("ÖZELLİKLER")
    print("=" * 60)
    for feature, desc in FEATURES.items():
        print(f"{feature}: {desc}")
    
    print("\n" + "=" * 60)
    print("KULLANIM ÖRNEKLERİ")
    print("=" * 60)
    for category, examples in USAGE_EXAMPLES.items():
        print(f"\n{category}:")
        for example in examples:
            print(f"  • {example}")


if __name__ == "__main__":
    print_structure()

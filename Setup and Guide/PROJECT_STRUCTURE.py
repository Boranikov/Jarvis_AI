"""
Jarvis AI Assistant - Proje Yapısı Özeti
"""

PROJECT_STRUCTURE = """
Jarvis_Aİ/
│
├── main.py                    # Ana uygulama - başlangıç noktası
├── config.py                  # Konfigürasyon dosyası (ayarları buradan düzenle)
├── utils.py                   # Yardımcı fonksiyonlar
├── setup.py                   # Kurulum betiği
├── requirements.txt           # Python bağımlılıkları
├── README.md                  # Proje dokümantasyonu
├── .gitignore                 # Git ignore kuralları
│
├── .vscode/
│   └── launch.json            # VS Code debug yapılandırması
│
├── brain/                     # NLP ve Intent Engine modülü
│   ├── __init__.py
│   ├── intent_engine.py       # LLM tabanlı intent tanıma
│   │   └── SYSTEM_PROMPT      # Ollama LLM için system prompt
│   └── memory.py              # Konuşma hafızası ve state yönetimi
│
└── Skills/                    # Eylem yöneticisi modülü
    ├── __init__.py
    └── skills_manager.py      # Aksiyonları gerçekleştir (dosya, müzik, vb.)
"""

MODULE_DESCRIPTIONS = {
    "main.py": "Ana program döngüsü ve kullanıcı etkileşimi yönetimi",
    
    "config.py": "Tüm konfigürasyon ayarları (keywords, prompts, vb.)",
    
    "utils.py": "Ortak yardımcı fonksiyonlar (name extraction, debugging)",
    
    "brain/intent_engine.py": """
    - Ollama LLM'i kullanarak user input'ı analiz eder
    - JSON formatında action ve parametreleri çıkarır
    - System prompt ile modeli yönlendirir
    """,
    
    "brain/memory.py": """
    - Konuşma geçmişini tutar (son 10 konuşma)
    - Bekleyen işlemleri (pending actions) yönetir
    - State ve session yönetimi
    """,
    
    "Skills/skills_manager.py": """
    - Dosya/klasör operasyonları (create, delete)
    - Spotify entegrasyonu (müzik çalma)
    - Web arama (Google)
    - Hata yönetimi ve logging
    """,
}

FEATURES = {
    "✓ NLP Intent Recognition": "Ollama LLM ile user input'ı analiz et",
    "✓ Dosya Yönetimi": "Dosya ve klasör oluştur/sil",
    "✓ Spotify Entegrasyonu": "Spotify'dan müzik çal",
    "✓ Web Arama": "Google'da ara",
    "✓ Konuşma Hafızası": "Son 10 konuşmayı hatırla",
    "✓ Dinamik Parametre Çıkartma": "User input'tan eksik parametreleri täyin et",
    "✓ Multi-step Actions": "Eksik parametreler için step-by-step sorgu",
    "✓ Error Handling": "Kapsamlı hata yönetimi ve logging",
}

USAGE_EXAMPLES = {
    "Dosya Oluşturma": [
        "jarvis, test.txt oluştur",
        "hey jarvis, my_document.docx yap",
    ],
    
    "Klasör Oluşturma": [
        "jarvis, yeni klasör oluştur",
        "my_folder klasörü oluştur",
    ],
    
    "Müzik Çalma": [
        "jarvis, tarkan çal",
        "spotify'dan gökhan türkmen çal",
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

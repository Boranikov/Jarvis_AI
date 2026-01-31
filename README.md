# Just A Rather Very Intelligent Servant (J.A.R.V.I.S)

Türkçe konuşan, yerel bir AI asistanı. Ollama LLM modeli üzerinde çalışır.

## Proje Yapısı

```
Jarvis_Aİ/
├── main.py                 # Ana uygulama
├── config.py              # Konfigürasyon dosyası
├── utils.py               # Yardımcı fonksiyonlar
├── requirements.txt       # Bağımlılıklar
├── README.md              # Dokümantasyon
│
├── brain/                 # NLP ve Intent Engine
│   ├── __init__.py
│   ├── intent_engine.py   # LLM tabanlı intent tanıma
│   └── memory.py          # Konuşma hafızası
│
└── Skills/                # Eylem yöneticisi
    ├── __init__.py
    └── skills_manager.py  # Aksiyonları gerçekleştir
```

## Kurulum

1. Gerekli kütüphaneleri yükle:
```bash
pip install -r requirements.txt
```

2. Ollama'yı kur ve `gemma2:2b` modelini indir:
```bash
ollama pull gemma2:2b
ollama serve
```

3. Uygulamayı çalıştır:
```bash
python main.py
```

## Özellikler

- 🎯 **Intent Recognition**: Kullanan girdisini NLP ile analiz et
- 📁 **Dosya Yönetimi**: Dosya/klasör oluştur ve sil
- 🎵 **Spotify Entegrasyonu**: Spotify'dan müzik çal
- 🔍 **Web Arama**: Google'da ara
- 💬 **Küçük Sohbet**: Genel sohbet
- 🧠 **Konuşma Hafızası**: Son 10 konuşmayı hatırla

## Komutlar

### Dosya Yönetimi
- "Jarvis, test.txt oluştur"
- "Jarvis, my_folder klasörü oluştur"
- "Jarvis, test.txt sil"
- "Jarvis, my_folder sil"

### Müzik
- "Jarvis, Tarkan çal"
- "Spotify'dan Gökhan Türkmen çal"

### Web Arama
- "Jarvis, Python ara"
- "Google'da AI ara"

### Sistem
- "Jarvis, orda mısın?" → Sistem status kontrolü
- "çık" veya "exit" → Programı kapat

## Konfigürasyon

`config.py` dosyasında ayarları özelleştirebilirsiniz:

- `LLM_MODEL`: Kullanan LLM modeli
- `LLM_TEMPERATURE`: Yaratıcılık seviyesi
- `ACTION_KEYWORDS`: Aksiyon tetikleyici kelimeler
- `DEBUG_MODE`: Hata ayıklama modu

## Geliştirme

Yeni özellik eklemek için:

1. `config.py`'de action tanımla
2. `brain/intent_engine.py`'de SYSTEM_PROMPT'u güncelle
3. `Skills/skills_manager.py`'ye işlemi ekle
4. `main.py`'de kontrol logikasını ekle

## Lisans

MIT License

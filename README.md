# Jarvis AI Assistant

Türkçe konuşan, yerel bir AI asistanı. Ollama LLM modeli üzerinde çalışır.

## Proje Yapısı

```
Jarvis_Aİ/
├── main.py                    # Ana uygulama (entry point)
├── config.py                  # Konfigürasyon dosyası
├── requirements.txt           # Bağımlılıklar
│
├── Core/                      # Ana işleme modülü
│   ├── handler.py             # Kullanıcı girdisi işleme
│   └── display.py             # UI ve çıktı fonksiyonları
│
├── Brain/                     # NLP ve Intent Engine
│   ├── intent_engine.py       # LLM tabanlı intent tanıma
│   └── memory.py              # Konuşma hafızası
│
├── Skills/                    # Beceri modülleri
│   ├── skills_manager.py      # Skill yönlendirici (router)
│   ├── file_skills.py         # Dosya/klasör işlemleri
│   ├── music_skills.py        # Müzik çalma
│   └── web_skills.py          # Web araması
│
└── Utils/                     # Yardımcı fonksiyonlar
    ├── paths.py               # Path işlemleri
    └── helpers.py             # Genel yardımcılar
```

## Kurulum

1. Gerekli kütüphaneleri yükle:
```bash
pip install -r requirements.txt
```

### 2. Yapay Zeka (Ollama) Modellerinin İndirilmesi
Jarvis gücünü Ollama üzerinden çalıştırılan model setlerinden alır.
Aşağıdaki modelleri bilgisayarınıza indirin (RAM'iniz en az 16GB, tercihen 32GB olmalıdır):
```bash
ollama pull qwen3:1.7b           # Hızlı otonom ajans modeli (ReAct)
ollama pull qwen2.5:7b           # Ağır muhakeme modeli
ollama pull qwen2.5-coder:14b    # Kodlama otonom modeli
ollama pull nomic-embed-text     # Hafıza Embedding (Metni vektöre çeviren RAG modeli)
```

### 3. API Anahtarları (.env Yapılandırması)
Ana dizindeki veya `dist/JarvisAI` klasöründeki `.env` dosyasını yapılandırın:
```env
# Spotify Bilgileriniz
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

# (Eğer kurulduysa) Diğer Entegrasyonlar
JARVIS_N8N_WEBHOOK_URL=http://.../webhook/jarvis
JARVIS_QDRANT_URL=http://...:6333
```

### 4. Çalıştırma
Jarvis 3 modda çalışabilir. Kullanacağınız amaca göre uygun komutu seçin:

**Mod 1: Arayüz (GUI)**
Hızlı, gri-siyah tonlarda şık, modern bir sohbet baloncuğu deneyimi sunar:
```bash
python main.py
```

## Özellikler

- 🎯 **Intent Recognition**: Kullanıcı girdisini NLP ile analiz et
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

### Müzik
- "Jarvis, Tarkan çal"
- "Sezen Aksu tükeneceğiz çal"

### Web Arama
- "Jarvis, Python ara"

### Sistem
- "Jarvis, orda mısın?" → Sistem kontrolü
- "çık" veya "exit" → Programı kapat

## Konfigürasyon

`config.py` dosyasında ayarları özelleştirebilirsiniz:

- `LLM_MODEL`: Kullanılan LLM modeli
- `LLM_TEMPERATURE`: Yaratıcılık seviyesi
- `DEBUG_MODE`: Hata ayıklama modu

## Geliştirme

Yeni özellik eklemek için:

1. `Skills/` altına yeni skill dosyası oluştur (örn: `weather_skills.py`)
2. `Skills/skills_manager.py`'deki `SKILL_MAP`'e ekle
3. `Brain/intent_engine.py`'deki `SYSTEM_PROMPT`'a action ekle

## Lisans

MIT License

# 🤖 Jarvis AI Assistant ( Just A Rather Very Intelligent Servent)

Türkçe konuşan, tamamen yerel olarak çalışan (Local LLM), modüler ve genişletilebilir bir kişisel AI asistanı.

> **3 Ayrı AI Modeli** · **Agentic Kodlama** · **Spotify Entegrasyon** · **PyQt6 GUI**

---

## Proje Yapısı

```
Jarvis_Aİ/
├── main.py                     # Uygulama giriş noktası (CLI/GUI)
├── config.py                   # Merkezi konfigürasyon
├── .env                        # API anahtarları (Spotify, OpenWeather)
├── requirements.txt            # Python bağımlılıkları
│
├── Brain/                      # 🧠 Zeka Katmanı
│   ├── router.py               # Intent sınıflandırma (coding/reasoning/fast)
│   ├── intent_engine.py        # Hızlı model — basit komutlar (qwen2.5:3b)
│   ├── reasoning_engine.py     # Düşünme modeli — karmaşık sorular (qwen2.5:7b)
│   ├── coding_engine.py        # Kodlama motoru — agentic loop (qwen2.5-coder:14b)
│   ├── plan_executor.py        # Çok adımlı planları sırayla yürütür
│   └── memory.py               # Konuşma hafızası ve bekleyen işlemler
│
├── Core/                       # ⚙️ Çekirdek Orkestrasyon
│   ├── handler.py              # Ana giriş işleyici (tüm trafik buradan geçer)
│   └── display.py              # CLI banner ve debug loglama
│
├── Skills/                     # 🛠️ Yetenekler
│   ├── skills_manager.py       # Aksiyon → Fonksiyon eşleştirme (Dispatcher)
│   ├── file_skills.py          # Dosya/klasör CRUD + okuma/yazma/listeleme
│   ├── music_skills.py         # Spotify: çal, durdur, devam et, geç, duygu bazlı
│   └── web_skills.py           # Google arama
│
├── UI/                         # 🖥️ Grafik Arayüzü (PyQt6)
│   ├── main_window.py          # Ana pencere ve sohbet arayüzü
│   ├── worker.py               # AI arka plan thread'i
│   ├── styles.qss              # Grayscale premium tema
│   └── widgets/                # Konuşma baloncukları
│
└── Utils/                      # 🔧 Yardımcılar
    ├── paths.py                # OS yolları (Desktop, Documents, Downloads)
    ├── helpers.py              # Metin temizleme
    └── math_validator.py       # LLM matematik doğrulaması (SymPy/NumPy)
```

## Kurulum

### 1. Gereksinimler
```bash
pip install -r requirements.txt
```

### 2. Ollama Modelleri
```bash
ollama pull qwen2.5:3b           # Hızlı model (basit komutlar)
ollama pull qwen2.5:7b           # Düşünme modeli (karmaşık sorular)
ollama pull qwen2.5-coder:14b    # Kodlama modeli (proje oluşturma, bug fix)
ollama serve
```

### 3. API Anahtarları
`.env` dosyasına Spotify ve OpenWeather API anahtarlarınızı ekleyin:
```env
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
OPENWEATHER_API_KEY=your_key
```

### 4. Çalıştırma
```bash
python main.py          # GUI modu (varsayılan)
python main.py --cli    # Konsol modu
```

## AI Modelleri ve Yönlendirme

| Model | Parametre | Rol | Tetikleyiciler |
|-------|-----------|-----|----------------|
| `qwen2.5:3b` | 3B | Hızlı komutlar | dosya/klasör oluştur, müzik çal, selamlaşma |
| `qwen2.5:7b` | 7B | Derin düşünme | "nedir?", duygu analizi, planlama, matematik |
| `qwen2.5-coder:14b` | 14B | Kodlama | "kodla", "bug", "refactor", "optimize et" |

```
Kullanıcı Girdisi → Router (classify_intent)
                        ├── "coding"    → CodingEngine (Agentic Loop)
                        ├── "reasoning" → ReasoningEngine (CoT + Plan Executor)
                        └── "fast"      → IntentEngine (JSON → Skill)
```

## Özellikler

- 💻 **Agentic Kodlama** — Model dosyaları okur, analiz eder, tam çalışan kod yazar
- 🧠 **Akıllı Yönlendirme** — 3 model arasında otomatik geçiş
- 📁 **Dosya Yönetimi** — Oluştur, sil, oku, yaz, klasör listele
- 🎵 **Spotify** — Müzik çal/durdur/geç, duygu bazlı öneri
- 🔢 **Matematik Doğrulama** — LLM cevaplarını SymPy/NumPy ile doğrular
- 😊 **Duygu Analizi** — Kullanıcı duygusunu algılar, empati gösterir
- 🖥️ **Modern GUI** — PyQt6 sohbet arayüzü, grayscale premium tema
- 💾 **Konuşma Hafızası** — Son 10 mesajı hatırlar

## Komutlar

| Kategori | Örnekler |
|----------|----------|
| **Dosya** | "test.txt oluştur", "masaüstüne proje klasörü aç" |
| **Müzik** | "Tarkan çal", "müziği durdur", "sıradaki şarkı" |
| **Arama** | "Python nedir araştır" |
| **Kodlama** | "yılan oyunu kodla", "main.py'deki hatayı bul" |
| **Sohbet** | "Nasılsın?", "sıkıldım ne yapayım?" |
| **Sistem** | "Jarvis orada mısın?", "çık" |

## Konfigürasyon

`config.py` içindeki temel ayarlar:

| Ayar | Değer | Açıklama |
|------|-------|----------|
| `FAST_MODEL` | `qwen2.5:3b` | Hızlı model |
| `REASONING_MODEL` | `qwen2.5:7b` | Düşünme modeli |
| `CODING_MODEL` | `qwen2.5-coder:14b` | Kodlama modeli |
| `MAX_TOOL_ITERATIONS` | `15` | Coding engine maks. araç çağrısı |
| `SAFETY_MODE` | `False` | Yazma/silme işlemleri için onay mekanizması |
| `MEMORY_HISTORY_LIMIT` | `10` | Hafızadaki maks. mesaj sayısı |
| `DEBUG_MODE` | `True` | Debug logları |

## Lisans

MIT License

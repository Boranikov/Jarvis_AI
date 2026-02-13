# Jarvis AI - Geliştirici El Kitabı (Developer Guide)

**Sürüm:** 2.0 (Production-Grade)
**Tarih:** 2026-02-12
**Yazarlar:** Google DeepMind & Boranikov

---

## 1. Proje Mimarisi ve Genel Bakış (High-Level Architecture)

### 1.1. Projenin Amacı
Jarvis AI, yerel olarak çalışan (Local LLM), Türkçe dil desteğine sahip, modüler ve genişletilebilir bir kişisel asistan projesidir. Temel amacı, kullanıcının doğal dildeki komutlarını anlayarak dosya yönetimi, müzik çalma, web araması, matematiksel hesaplama ve karmaşık planlama görevlerini yerine getirmektir.

### 1.2. Tasarım Kalıpları (Design Patterns)
Proje, bakımı kolay ve ölçeklenebilir olması için aşağıdaki tasarım kalıplarını kullanır:

- **Modular Monolith:** Fonksiyonlar mantıksal modüllere (`Brain`, `Core`, `Skills`, `UI`, `Utils`) ayrılmıştır, ancak tek bir deploy edilebilir ünite halindedir.
- **Strategy Pattern (Skills):** Her bir yetenek (örn: `create_file`, `play_music`) bağımsız bir strateji olarak uygulanır ve `skills_manager.py` tarafından yönetilir.
- **Factory / Disclaimer Pattern (Router):** `Brain/router.py`, gelen isteği analiz eder ve uygun işlem motoruna (Fast Model vs. Reasoning Model) yönlendirir.
- **Observer Pattern (UI):** PyQt6 sinyal-slot mekanizması (`UI/worker.py`), arka plan işlemlerini UI thread'inden ayırmak için kullanılır.
- **Singleton-ish Configuration:** `config.py` modülü, uygulama genelinde tekil ve değişmez (immutable) konfigürasyon sağlar.

### 1.3. Veri Akışı (Data Flow)
1. **Girdi:** Kullanıcı `main.py` (CLI veya GUI) üzerinden komut gönderir.
2. **Orkestrasyon (`Core/handler.py`):** `process_input` fonksiyonu isteği karşılar.
3. **Yönlendirme (`Brain/router.py`):** İstek analiz edilir:
    *   *Basit Komutlar:* `Brain/intent_engine.py` (Hızlı Model) → JSON çıktı.
    *   *Karmaşık/Duygusal:* `Brain/reasoning_engine.py` (Düşünme Modeli) → Plan ve JSON çıktı.
4. **Yürütme (`Brain/plan_executor.py`):** Çıkarılan aksiyonlar ve parametreler işlenir.
5. **Yetenek Kullanımı (`Skills/*`):** `skills_manager.py` üzerinden ilgili fonksiyon çağrılır.
6. **Çıktı:** Sonuç kullanıcıya metin veya görsel (GUI) olarak döner.

---

## 2. Dosya ve Dizin Yapısı (File Structure & Map)

```text
Jarvis_AI/
├── Brain/                  # BEYİN: Karar verme, NLP ve Hafıza
│   ├── intent_engine.py    # Basit niyetleri (intent) hızlıca anlar (JSON üretir).
│   ├── reasoning_engine.py # Karmaşık sorunları düşünür ve planlar (CoT).
│   ├── router.py           # İsteği analiz eder ve doğru motora yönlendirir (Traffic Cop).
│   ├── plan_executor.py    # Reasoning motorundan gelen adımları sırayla işletir.
│   └── memory.py           # Konuşma geçmişini ve bekleyen işlemleri (session) tutar.
│
├── Core/                   # ÇEKİRDEK: Orkestrasyon ve Temel İşlevler
│   ├── handler.py          # Girdi işleme merkezi. BÜTÜN trafik buradan geçer.
│   └── display.py          # Konsol çıktıları ve loglama yardımcıları.
│
├── Skills/                 # YETENEKLER: Dış dünya ile etkileşim
│   ├── file_skills.py      # Dosya/Klasör oluşturma ve silme işlemleri.
│   ├── music_skills.py     # Spotify vb. müzik çalma entegrasyonu.
│   ├── web_skills.py       # Google arama ve tarayıcı işlemleri.
│   └── skills_manager.py   # Aksiyon isminden fonksiyona yönlendirme (Dispatcher).
│
├── UI/                     # ARAYÜZ (Kullanıcı etkileşimi)
│   ├── main_window.py      # PyQt6 ana pencere tasarımı ve olayları.
│   ├── worker.py           # Arka plan thread'i (UI donmasını engeller).
│   └── widgets/            # Özel UI bileşenleri (örn: konuşma balonları).
│
├── Utils/                  # ARAÇLAR: Yardımcı fonksiyonlar
│   ├── helpers.py          # Metin temizleme vb. genel yardımcılar.
│   ├── paths.py            # İşletim sistemi yollarını (Desktop, Docs) çözer.
│   └── math_validator.py   # LLM matematik yanıtlarını doğrular (SymPy/NumPy).
│
├── config.py               # AYARLAR: Sabitler, Prompts ve Loglama (Immutable).
├── main.py                 # GİRİŞ: Uygulamanın başlangıç noktası (CLI/GUI seçimi).
└── requirements.txt        # BAĞIMLILIKLAR: Gerekli Python paketleri.
```

---

## 3. Kritik Modüller ve Sorumlulukları

### 3.1. Giriş İşleyici (`Core/handler.py`)
Projenin kalbidir. Hem CLI hem de GUI modlarından gelen istekleri tek bir `process_input(user_input, memory, mode)` fonksiyonunda birleştirir.
*   **Sorumlulukları:** Presence check ("Jarvis orada mısın?"), Router çağırma, Model seçimi, Skill çalıştırma ve Hafıza güncelleme.
*   **DRY Prensibi:** Çıktı formatı `OutputMode` Enum'ı ile yönetilir (CLI için print, GUI için return string).

### 3.2. Hafıza Yönetimi (`Brain/memory.py`)
Oturum süresince (session-based) çalışır.
*   **Yapı:** `collections.deque(maxlen=N)` kullanır. Bu sayede hafıza limiti aşıldığında en eski kayıt otomatik silinir (O(1)).
*   **Pending Actions:** Eksik parametreleri (örn: dosya adı verilmemişse) tutar ve bir sonraki turda tamamlar.

### 3.3. Hata Yönetimi ve Güvenlik
*   **Spesifik Exception Handling:** `except Exception` yerine `OSError`, `PermissionError`, `JSONDecodeError` gibi spesifik hatalar yakalanır.
*   **Logging:** `print()` yerine Python `logging` modülü kullanılır. Loglar `config.py` üzerinden yönetilir.
*   **Güvenli Matematik:** `eval()` fonksiyonu **KESİNLİKLE YASAKTIR**. Yerine `Utils/math_validator.py` içindeki `_safe_eval` (AST-whitelist) veya `SymPy` kullanılır.
*   **Resource Management:** Dosya işlemlerinde mutlaka `with open(...)` (Context Manager) kullanılır.

---

## 4. Genişletilebilirlik Rehberi (Extensibility Guide)

### Senaryo A: Yeni Bir "Yetenek/Skill" Eklemek (Örn: E-mail Gönderme)

1.  **Yeni Dosya Oluştur:** `Skills/email_skills.py` dosyasını oluşturun.
2.  **Fonksiyonu Yaz:**
    ```python
    def send_email(params: dict) -> bool:
        """E-mail gönderir. Params: 'to', 'subject', 'body'."""
        # Validasyon ve işlem kodları...
        # Resource yönetimi ve logging unutma!
        return True
    ```
3.  **Skills Manager'a Kaydet:**
    *   `Skills/skills_manager.py` dosyasını açın.
    *   Fonksiyonu import edin.
    *   `SKILL_MAP` sözlüğüne ekleyin: `"send_email": send_email`.
4.  **Modeli Eğit (System Prompt):**
    *   `Brain/intent_engine.py` (Fast Model) ve/veya `Brain/reasoning_engine.py` (Reasoning Model) içindeki `SYSTEM_PROMPT` değişkenine yeni aksiyonu ve parametre formatını ekleyin.

### Senaryo B: Yeni Bir AI Modeli Entegre Etmek

1.  **Config Güncelle:** `config.py` dosyasına model ismini ekleyin (örn: `VISION_MODEL = "llava:latest"`).
2.  **Motor Entegrasyonu:** Eğer yeni bir yetenek seti geliyorsa (örn: görsel analiz), `Brain/` altında `vision_engine.py` oluşturun.
3.  **Router Güncelle:** `Brain/router.py` içindeki `classify_intent` mantığına, isteğin görsel analiz gerektirip gerektirmediğini anlayan bir kural (örn: "resim", "fotoğraf" kelimeleri) ekleyin.

### Senaryo C: Yeni Bir API/Endpoint Eklemek

Jarvis şu an lokal çalışır. Eğer bir REST API sunmak isterseniz:
1.  **FastAPI/Flask:** `main.py` yanına `server.py` ekleyin.
2.  **Endpoint Bağlantısı:** API endpoint'i, `Core.handler.process_input` fonksiyonunu `OutputMode.GUI` (string return) moduyla çağırmalıdır.

---

## 5. Kod Standartları ve Kurallar

1.  **Type Hinting:** **ZORUNLUDUR.** Her fonksiyonun parametreleri ve dönüş tipi belirtilmelidir.
    *   ✅ `def connect(url: str, retry: int = 3) -> bool:`
    *   ❌ `def connect(url, retry=3):`
2.  **Docstrings:** Her modül, sınıf ve fonksiyonun ne işe yaradığını anlatan kısa, öz bir docstring'i olmalıdır. Uzun ve gereksiz "Optimizasyon" notları kod içine değil, PR açıklamalarına yazılmalıdır.
3.  **Logging:** `print()` kullanmayın. `config.get_logger(__name__)` ile logger oluşturun ve `logger.info()`, `logger.error()` kullanın.
4.  **Performans:**
    *   Listede arama (`x in list`) yerine `set` veya `frozenset` kullanın (O(1)).
    *   String birleştirmelerde döngü içinde `+=` yerine `list.append()` ve `"".join()` kullanın.
5.  **İsimlendirme:**
    *   Değişkenler/Fonksiyonlar: `snake_case` (örn: `calculate_total`)
    *   Sınıflar: `PascalCase` (örn: `ReasoningEngine`)
    *   Sabitler: `UPPER_CASE` (örn: `MAX_RETRIES`)

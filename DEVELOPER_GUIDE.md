# Jarvis AI - Geliştirici El Kitabı (Developer Guide)

**Sürüm:** 3.0 (Coding Engine Entegrasyonu)
**Tarih:** 2026-02-19
**Yazarlar:** Google DeepMind & Boranikov

---

## 1. Mimari Genel Bakış

### 1.1. Katmanlı Yapı

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (Entry Point)                 │
│                     CLI / GUI Seçimi                     │
├─────────────────────────────────────────────────────────┤
│                Core/handler.py (Orkestratör)             │
│           process_input(text, memory, mode)              │
├──────────┬──────────────┬───────────────┬───────────────┤
│  Router  │  Fast Engine  │ Reasoning Eng │ Coding Engine │
│ (router  │ (intent_      │ (reasoning_   │ (coding_      │
│  .py)    │  engine.py)   │  engine.py)   │  engine.py)   │
│          │  qwen2.5:3b   │  qwen2.5:7b   │  coder:14b    │
├──────────┴──────────────┴───────────────┴───────────────┤
│            Skills (file, music, web) + Utils             │
└─────────────────────────────────────────────────────────┘
```

### 1.2. Tasarım Kalıpları

| Pattern | Nerede | Açıklama |
|---------|--------|----------|
| **Strategy** | `Skills/` | Her skill bağımsız bir strateji, `SKILL_MAP` ile dispatch |
| **Router** | `Brain/router.py` | Intent sınıflandırma ile doğru motora yönlendirme |
| **Agentic Loop** | `Brain/coding_engine.py` | Model kendi kendine araç çağırarak görev tamamlar |
| **Observer** | `UI/worker.py` | PyQt6 sinyal-slot ile thread-safe UI güncellemesi |
| **Immutable Config** | `config.py` | `MappingProxyType` ve `frozenset` ile değiştirilemez sabitler |

### 1.3. Veri Akışı

```
Kullanıcı → main.py → handler.process_input()
                           │
                           ├→ router.classify_intent()
                           │     ├── "coding"    ─→ coding_engine.process_coding_task()
                           │     │                    ├── [Loop] read_file → write_to_file
                           │     │                    └── final_answer
                           │     ├── "reasoning" ─→ reasoning_engine.process_reasoning()
                           │     │                    └── plan_executor.execute_plan()
                           │     └── "fast"      ─→ intent_engine.process_command()
                           │                          └── skills_manager.perform_skill()
                           │
                           └→ memory.add(input, response)
```

---

## 2. Modül Detayları

### 2.1. Router (`Brain/router.py`)

`classify_intent(user_input) → "coding" | "reasoning" | "fast"`

**Öncelik sırası:**
1. **Kodlama** — `_CODING_KEYWORDS` + `_CODING_PHRASE_TRIGGERS`
2. **Soru işareti** — `?` varsa reasoning (basit sorular hariç)
3. **Duygu** — `_EMOTION_KEYWORD_MAP` + `_EMOTION_PHRASE_MAP`
4. **Reasoning** — `_REASONING_WORD_TRIGGERS`
5. **Çoklu işlem** — `"ve"` bağlacı + sıralı ifadeler
6. **Matematik** — Operatörler, regex paterni
7. **Hızlı aksiyon** — `_FAST_ACTION_KEYWORDS`
8. **Varsayılan** — `"fast"`

Ek fonksiyon: `detect_emotion(user_input)` → `{detected, category, keywords}`

### 2.2. Motorlar

#### Fast Engine (`Brain/intent_engine.py`)
- **Model:** `qwen2.5:3b`
- **Görev:** Basit komutları JSON'a çevir (`action`, `path`, `name`, `song_name`)
- **Desteklenen aksiyonlar:** `create_file`, `create_folder`, `delete_file`, `delete_folder`, `play_music`, `pause_music`, `web_search`, `small_talk`, `get_weather`

#### Reasoning Engine (`Brain/reasoning_engine.py`)
- **Model:** `qwen2.5:7b`
- **Görev:** Karmaşık istekleri düşün, planla, duygu analizi yap
- **Çıktı türleri:** `answer`, `plan`, `suggestion`, `empathy`
- **Özellik:** `executable_steps` üretir → `plan_executor.py` ile çalıştırılır

#### Coding Engine (`Brain/coding_engine.py`)
- **Model:** `qwen2.5-coder:14b`
- **Görev:** Proje oluştur, kod yaz, bug çöz, dosya sistemiyle etkileşim
- **Çalışma prensibi:** Agentic Loop
  1. Model JSON döner: `{tool, args, thought}`
  2. Handler aracı çalıştırır: `perform_skill(tool, args)`
  3. Sonuç modele geri gönderilir
  4. `final_answer` gelene kadar döngü devam eder
- **Güvenlik:** `SAFETY_MODE=True` ise `write_to_file`/`delete_file` için kullanıcı onayı istenir
- **Format kurtarma:** JSON bozulursa `_FORMAT_CORRECTION_PROMPT` ile otomatik düzeltme (maks. `MAX_FORMAT_RETRIES` deneme)
- **Döngü limiti:** `MAX_TOOL_ITERATIONS` (varsayılan: 15)

### 2.3. Handler (`Core/handler.py`)

Projenin kalbi. Tüm trafik buradan geçer.

```python
process_input(user_input, memory, mode) → Optional[str]
```

- `OutputMode.CLI` → stdout'a print, `None` döner
- `OutputMode.GUI` → String döner (UI'a gönderilir)

İç fonksiyonlar:
- `_handle_coding()` → Agentic coding döngüsü
- `_handle_reasoning()` → CoT + plan executor + matematik doğrulama
- `_handle_fast_model()` → Intent parse + skill dispatch

### 2.4. Skills (`Skills/`)

`SKILL_MAP` üzerinden dispatch edilen 12 yetenek:

| Skill | Fonksiyon | Kaynak |
|-------|-----------|--------|
| `create_file` | Dosya oluştur | `file_skills.py` |
| `create_folder` | Klasör oluştur | `file_skills.py` |
| `delete_file` | Dosya sil | `file_skills.py` |
| `delete_folder` | Klasör sil | `file_skills.py` |
| `read_file` | Dosya içeriği oku | `file_skills.py` |
| `write_to_file` | Dosyaya yaz | `file_skills.py` |
| `list_dir_recursive` | Klasör ağacı listele | `file_skills.py` |
| `play_music` | Spotify'da çal | `music_skills.py` |
| `pause_music` | Müzik duraklat | `music_skills.py` |
| `resume_music` | Müzik devam ettir | `music_skills.py` |
| `next_track` | Sonraki şarkı | `music_skills.py` |
| `get_current_track` | Çalan şarkı bilgisi | `music_skills.py` |

### 2.5. Hafıza (`Brain/memory.py`)

- **Yapı:** `collections.deque(maxlen=MEMORY_HISTORY_LIMIT)`
- **Pending Actions:** Eksik parametre durumunda işlemi tutar, sonraki turda tamamlar
- **Session-based:** Uygulama kapandığında sıfırlanır

### 2.6. UI (`UI/`)

- **Framework:** PyQt6
- **Tema:** `styles.qss` (grayscale premium)
- **Thread:** `AIWorker(QThread)` — AI işlemleri arka planda, UI donmaz
- **Bileşenler:** `MainWindow` + `ChatBubble` widget'ı

---

## 3. Hata Yönetimi ve Güvenlik

| Kural | Detay |
|-------|-------|
| **Spesifik Exceptions** | `OSError`, `PermissionError`, `JSONDecodeError` — genel `Exception` son savunma |
| **Logging** | `config.get_logger(name)` → `logger.info/error/debug` |
| **Güvenli Matematik** | `eval()` **YASAK**. `math_validator.py` → AST whitelist + SymPy |
| **Context Manager** | Dosya işlemlerinde `with open(...)` zorunlu |
| **Coding Safety** | `SAFETY_MODE=True` → yazma/silme onayı gerektirir |

---

## 4. Genişletilebilirlik Rehberi

### Yeni Skill Eklemek

1. `Skills/` altına dosya oluştur (örn: `email_skills.py`)
2. Fonksiyon yaz: `def send_email(params: dict) -> bool:`
3. `skills_manager.py` → import + `SKILL_MAP`'e ekle
4. `intent_engine.py` ve/veya `reasoning_engine.py` → `SYSTEM_PROMPT`'a aksiyon ekle

### Yeni AI Modeli Eklemek

1. `config.py` → `NEW_MODEL = "model_adı"` ekle
2. `Brain/` altına motor dosyası oluştur (örn: `vision_engine.py`)
3. `Brain/router.py` → `classify_intent`'e yeni rota ekle
4. `Core/handler.py` → `_handle_new_model()` fonksiyonu ekle

### Yeni API Endpoint Eklemek

1. `server.py` oluştur (FastAPI/Flask)
2. Endpoint'ler `Core.handler.process_input(text, memory, OutputMode.GUI)` çağırsın

---

## 5. Kod Standartları

| Standart | Kural |
|----------|-------|
| **Type Hints** | Tüm fonksiyonlarda zorunlu |
| **Logging** | `print()` yerine `logger.info/error/debug` |
| **Veri yapıları** | `list` arama yerine `frozenset` (O(1)) |
| **İsimlendirme** | Değişkenler: `snake_case`, Sınıflar: `PascalCase`, Sabitler: `UPPER_CASE` |
| **Docstring** | Her fonksiyona kısa, öz docstring yaz |

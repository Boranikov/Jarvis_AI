# 🛠️ Jarvis AI — Geliştirici & AI Sistem Mimari Kılavuzu (Developer Guide)

Bu doküman projeye katkı sağlamak isteyen yazılım geliştiriciler (Human Developers) ve **Sistemi inceleyip kod değiştirecek AI Agent Kodlayıcılar** için kaynak bir mimari haritasıdır. Kodların genel davranış kalıplarını, klasör mantıklarını ve nasıl veri aktardıklarını içerir.

> Yeni bir Skill (yetenek) eklerken veya çekirdek (Core) bir değişiklik yaparken lütfen aşağıdaki hiyerarşik yapıya uygun hareket edin!

---

## 🏛️ 1. Genel Mimari (Klasör Ağacı ve İstek Yaşam Döngüsü)

Sistem bir ağ ve yönlendirme mantığı üzerine dizayn edilmiştir: `Girdi` → `Hafıza Kontrol` → `Yönlendirme (Router)` → `İlgili Model ve Motor (Engine)` → `Uygulama (Skill/Plan)` → `Yanıt`

```text
Jarvis_Aİ/
├── main.py                     # Ana başlatıcı (GUI veya CLI Modlarını tetikler)
├── jarvis_tray.py              # Background (System Tray) Uygulama başlatıcısı
├── build_exe.py / .spec'ler    # Projeyi Pyinstaller ile exe yapısını derleyen scriptler
├── config.py / Config/         # Sistem sabitleri (Promptlar, Log ayarları, API Modelleri vs.)
├── .env                        # Private Secret değişkenler (Token vb.)
│
├── Brain/                      # BEYİN: Tüm Karar ve Karakter (LLM İstekleri Çözer)
│   ├── router.py               # Ön Filtre. Metinden (coding, reasoning, fast) tip çıkarır.
│   ├── intent_engine.py        # [3B Model] Basit stringleri JSON'a (action/params) çevirir.
│   ├── reasoning_engine.py     # [7B Model] Sorgu, soru, empati ve Plan (Array<Dict>) çıkarır.
│   ├── coding_engine.py        # [14B Model] Asıl Kodlayıcı ajan loopu. Kendisi 'Skill' tetikler.
│   ├── plan_executor.py        # Reasoning'in plan dökümlerini sırayla Skills/ aktarır.
│   └── memory.py               # Conversation state. Eksik parametre ve sobet dizisi burada tutulur.
│
├── Core/                       # İSKELET: Beyni ve Beden'i birleştiren Handler Dosyaları.
│   ├── handler.py              # Senkron İşlem Motoru (Arayüzde ve CLI'de kullanılan ana yoldur).
│   └── async_handler.py        # Asenkron İşlem Motoru (Server'dan Webhook ile asenkron yürütmeler yapar).
│
├── Server/                     # DIŞ DÜNYA (GİRİŞ KAPISI): FastAPI Yapılandırması 
│   ├── app.py                  # http://0.0.0.0:8000 (Trafik ve Router yapısı).
│   ├── dependencies.py         # Lifespan events alanları, Context yönetimleri.
│   └── schemas.py              # Pydantic Tip doğrulayıcı Modelleri (ChatRequest vb).
│
├── Skills/                     # ELLER & BEDEN: FİZİKSEL EYLEMLER. Modelle JSON Eşleşir.
│   ├── skills_manager.py       # Switch-Case yapısıyla gelen action id'yi ilgili fonksiyona paslar.
│   ├── file_skills.py          # os, shell vb işlemleri I/O tarafı.
│   ├── music_skills.py         # Spotify Spotipy client API modülü.
│   └── (web_skills.py)         # İnternet/Araştırma yetenek modülleri (Varsa).
│
├── Integrations/ & MCP/       # UZAK SUNUCU (Entegrasyon / Data Layer)
│   ├── qdrant_client.py        # Vectör Store. (Uzun hafıza arama tarama).
│   └── notification_tools.py   # MCP standardına göre tasarlanmış tools bildirim yapısı.
│
├── UI/                         # PyQt6 Arayüz Dosyaları
│   ├── main_window.py          # Frontend Thread.
│   ├── worker.py               # Arayüz donmasın diye LLM İsteklerini taşıyan arka plan Thread'i.
│   └── ...
└── Utils/                      # Yardımcı Ortak Sınıflar & Fonksiyonlar (Örn: Matematik Sembol Doğrulayıcı).
```

---

## ⚙️ 2. Veri ve İstek Akışı Nasıl İşliyor? (Lifecycle)

Sisteme bir komut verildiğinde (İster terminalden ister Telegram API'nden), bu girdinin izlediği yol şöyledir:

1. **Ön-Filtre (Pre-filter):** `Core/handler.py` veya `async_handler.py` içinde, isteğin içinde bir "sistem varlık kontrolü" (Presence) olup olmadığına (Örn: "Jarvis orda mısın") bakılır. Değilse `Memory`'deki "Eksik parametre bekleniyor mu?" sekmesine bakar (Eksik işlem tamamlama loop'u).
2. **Router (`Brain/router.py`):** Girdi buraya paslanır. Keyword eşleştirmesi, regex tespitleri veya duygu saptaması (O(T) Token Check) ile isteğin "Tipi" (`coding`, `reasoning` veya `fast`) iade edilir.
3. **Engine Tetiklenmesi:**
    * **Fast (Skill):** `Brain/intent_engine.py` ile sadece ufak `3B` modeli çalışır, komutu JSON yapar. JSON içerisindeki `action` (ör: `play_music`) doğrudan `Skiil_Manager` -> `music_skills.py` dosyasına fırlatılır. `play_music()` gerçekte kodu çalıştırır. Biter. Geri JSON reply'si döner.
    * **Reasoning:** `Brain/reasoning_engine.py` içindeki `7B` modeliyle analiz edilir. Model empatik bir string ile beraber bir dizi sıralı `executable_steps` (Yaptırılacak işlemler listesi JSON) gönderebilir. Eğer bu liste doluysa `Core/handler.py` anında `plan_executor.py` üzerinden bunu loop'a sokarak Skills'leri sırayla çağırır.
    * **Coding:** `Brain/coding_engine.py` içindeki güçlü `14B` modele fırlatılır. Bu engine LLM'in tamamen kontrolde olduğu (Agentic) Loop'tır. Yapay zeka, doğrudan `create_file`, `write_to_file` gibi "Skills" modüllerini sanki kendi de bir insanmış gibi **Agent olarak doğrudan bir parametre** ile çağırır, çıkan terminal loglarını ve Python trace loglarını geri LLM prompt'una bağlayıp döngüde kontrol eder (Maks = 15 döngü). Onay mekanizmasına tabidir (Güvenlik için).

---

## 🏗️ 3. Yeni Bir Yetenek (Skill) Nasıl Eklenir?

Diyelim ki Jarvis'e *"Hava Durumunu Söyle"* özelliği eklemek istiyorsunuz. Bunu sisteme gömmek için şu senaryoları takip etmelisiniz:

### Adım 1: Yeni Python Modülünü ve Fonksiyonunu Oluştur (Fiziksel Eylem)
`Skills/` dizinine yeni dosya veya uygun dosya (`weather_skills.py`) aç.
Gerçek işi yapacak fonksiyonu kodla.
```python
def get_weather(city: str) -> str:
    # API'ye bağlanıp değer çekme vs..
    return f"{city} için hava durumu 22 Derece Güneşli."
```

### Adım 2: Onu Dispatcher'a Tanıt (`Skills/skills_manager.py`)
Yapay Zekanın bu `action` adıyla göndereceği isteği, 1. adımda yazdığın koda bağla.
```python
from Skills.weather_skills import get_weather

def perform_skill(action: str, parameters: dict) -> any:
    # ....
    elif action == "get_weather":
        city = parameters.get("city")
        return get_weather(city)
```

### Adım 3: LLM'leri Haberdar Et! (Kritik)
Jarvis'in beyni, yeni yeteneğinden JSON ortamında haberdar olmalı:
Yani `Brain/intent_engine.py` içerisindeki _SYSTEM_PROMPT_ stringine inin.
`=== ALLOWED ACTIONS ===` listesine `get_weather` id'sini dahil edin.
Örnek listesine de ekleyerek LLM'i finetune (few-shot-prompt) edin. (Örn: Modelden şöyle dönmesini bekle `{"action":"get_weather", "parameters":{"city":"istanbul"}}`).

Aynı güncellemeyi eğer isterseniz (Model bunu karmaşık akıllarda planlı kullansın istiyorsanız) `Brain/reasoning_engine.py` dosyasındaki Sistem Promptunun `Kullanabileceğin aksiyonlar:` alanına da aynen öğretin. O da bu skilli kullanarak plan yapabilsin!

### Adım 4: Eksik parametre ve Router'ı Güncelle (Son ayar)
Kullanıcı sadece "Hava durumunu söyle" dedi (İstanbul olduğunu yazmadı).
Memory de pending'e düşmesi için, `Config/config.py` içinde;
`REQUIRED_PARAMS["get_weather"] = ("city",)` 
`MISSING_QUESTIONS["get_weather"] = {"city": "Hangi şehrin hava durumunu öğrenmek istiyorsunuz Efendim?"}` sözlüklerini (Dict) güncelleyip öğretin.
Son olarak `Brain/router.py` dosyasında `_FAST_ACTION_KEYWORDS` set() içine `"hava","havayı"` kelimesini ekleyerek, kullanıcının cümlesinin doğrudan `get_weather` engine'e düşmesini sağlayın. (Reasoning olup kaybolmasını engellemek için)

İşleminiz bitti! Yeni özellik artık Jarvis'te aktif.

---

> 🎉 **Bu Kuralları Okuyan AI Kodlayıcı ve Asistanlara Uyarı:**
> Jarvis'in dosya isimlerini veya kodlama mantığını değiştirirken, *kesinlikle* API Controllerlarını, Prompt yapılarını ve System Instruction'larını aynı hizada güncellemeyi unutmayın. Sistemin kararlılığı Prompt Injection ve Prompt Formatına dayalı çalışmaktadır!

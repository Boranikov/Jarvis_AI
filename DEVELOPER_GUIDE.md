# 🛠️ Jarvis AI — Geliştirici & AI Sistem Mimari Kılavuzu (Developer Guide)

Bu doküman projeye katkı sağlamak isteyen yazılım geliştiriciler (Human Developers) ve **Sistemi inceleyip kod değiştirecek AI Ajan Kodlayıcılar** için kaynak bir mimari haritasıdır. Kodların genel davranış kalıplarını, klasör mantıklarını ve nasıl veri aktardıklarını içerir.

> Yeni bir Skill (yetenek) eklerken veya çekirdek (Core) bir değişiklik yaparken lütfen LangGraph ve MCP (Model Context Protocol) hiyerarşik yapısına uygun hareket edin!

---

## 🏛️ 1. Genel Mimari (Klasör Ağacı ve İstek Yaşam Döngüsü)

Sistem, LangChain/LangGraph kütüphanelerinin ReAct (Reasoning & Acting) ajan tabanlı otomasyon yapısıyla "Tool Calling" yönlendirme mantığı üzerine dizayn edilmiştir:

`Girdi` → `FastAPI/CLI Handler` → `LangGraph (Agent Node)` → `Tool İhtiyacı Varsa (MCP/Skills)` → `Tool Node` → `Tekrar Agent Node` → `Yanıt`

```text
Jarvis_Aİ/
├── main.py                     # Ana başlatıcı (GUI veya CLI Modlarını tetikler)
├── jarvis_tray.py              # Background (System Tray) Uygulama başlatıcısı
├── Config/                     # Sistem sabitleri (Promptlar, Log ayarları, API Modelleri vs.)
├── .env                        # Private Secret değişkenler (Token vb.)
├── Scripts/                    # Derleme ve yayınlama (PyInstaller .spec) betikleri
├── Tests/                      # Geliştirici unit/integration testleri
│
├── Brain/                      # BEYİN: Tüm Karar ve Karakter (LLM İstekleri Çözer)
│   ├── graph_router.py         # LangGraph StateGraph Orkestratörü (app iade eder).
│   ├── graph_nodes.py          # Sistem Agent düğümünü (qwen3) ve Tool düğümünü tutar.
│   ├── graph_state.py          # State yapısını (JarvisState) tanımlar.
│   ├── reasoning_engine.py     # Çok aşamalı, karmaşık "plan çıkarılacak" durumları ayrıştırır.
│   ├── coding_engine.py        # Kendi tool'larını döngü içerisinde bağımsız çalıştıran Otonom Kodlayıcı.
│   └── memory.py               # Session (Oturum) bazlı geçici tarihçe yöneticisi.
│
├── Core/                       # İSKELET: Beyni ve Beden'i birleştiren Handler Dosyaları.
│   ├── handler.py              # LangGraph orkestratörünü Senkron işleyen GUI motoru.
│   ├── async_handler.py        # LangGraph ainvoke() tetikleyen Asenkron FastAPI motoru.
│   └── schema_generator.py     # Kodlardaki yetenekleri LLM JSON'ına çeviren analizör.
│
├── Server/                     # DIŞ DÜNYA (GİRİŞ KAPISI): FastAPI Yapılandırması 
│   ├── app.py                  # http://0.0.0.0:8000 (Trafik ve Router yapısı).
│   └── dependencies.py         # Lifespan events alanları, FastMCP başlatıcısı.
│
├── Skills/                     # ELLER & BEDEN: FİZİKSEL EYLEMLER. Modellerin asıl araçları.
│   ├── skills_manager.py       # Switch-Case yapısıyla gelen action id'yi ilgili fonksiyona paslar.
│   ├── file_skills.py          # os, shell vb fiziksel I/O ve disk okuma/yazma işlemleri.
│   ├── music_skills.py         # Spotify Spotipy client API modülü.
│   └── terminal_skills.py      # shell exec motorları.
│
└── MCP/                        # MODEL CONTEXT PROTOCOL (Dış Sistem Bağlantıları)
    ├── tool_registry.py        # FastMCP araçlarını tutan, LangGraph LLM tool çağrılarını asenkron/senkron bağlayan adaptör.
    └── tools/
        ├── memory_tools.py     # Qdrant Vektör Tabanlı "search_long_term_memory" araçları.
        ├── cloud_tools.py      # Nextcloud webdav üzerinden dosya işlem araçları.
        └── notification_tools.py # n8n üzerinden dışarıya asenkron ping atan mesaj araçları.
```

---

## ⚙️ 2. Veri ve İstek Akışı Nasıl İşliyor? (Lifecycle)

Sisteme terminalden veya sunucudan komut verildiğinde (Örn: "Daha önce adımın ne olduğunu hatırlıyor musun?"), bu girdinin izlediği yol şöyledir:

1. **Ön-Filtre (Presence Persistence):** `Core/handler.py` içinde, isteğin içinde bir "sistem varlık kontrolü" ("Jarvis orda mısın") var mı bakılır. Eğer varsa, hiç LLM'e gitmeden doğrudan "Sizin için her zaman buradayım efendim" yanıtı döner.
2. **Semantic Router (Niyet Analizi):** Girdi `Brain/router.py` üzerinden `semantic-router` ve embedding'ler (Ollama) ile sınıflandırılır (`coding`, `reasoning`, `fast`).
3. **LangGraph StateGraph Başlatılması (`Brain/graph_router.py`):** Girdi `HumanMessage` olarak paketlenir ve `JarvisState` durumuna (State array) konulur.
3. **Agent Node (`Brain/graph_nodes.py`):**
    * Sistem, güçlü bir `SystemMessage` promptuyla `Qwen3:1.7b` (Küçük fakat tool-calling yeteneği yüksek model) modelini tetikler.
    * Qwen iç yapısındaki `thinking` (muhakeme) sürecini kullanarak bu string isteğine karşılık "Benim bunu aklımda aratmam lazım" der.
    * İşleminin çıktısı olarak bir `AIMessage` döndürür ve objesinde **"tool_calls"** barındırır. (Çağırdığı Tool ID: `search_long_term_memory`).
4. **Conditional Edge / Tool Yönlendirici:** StateGraph'daki Router bakar: Model Tool Çağırmış mı? Çağırdıysa Rotayı `Tool Node`'a kaydırır.
5. **Tool Node (`Skills/skills_manager.py` ve `MCP/tool_registry.py`):**
    * Çağırılan fonksiyon `memory_tools` MCP sekmesi içinden çekilir, parametreler paslanır. Qdrant veritabanına sorgu atılır. Dönen bilgi string olarak grafiğe geri yüklenir.
    * Grafiğin ucu tekrar `Agent Node`'a basılır.
6. **Final Yanıt ve Kapatma:** LLM, veri tabanından gelen çıktıyı kendi konuşma diline derleyip Türkçe olarak `AIMessage` şeklinde dışarı kusar. Arkasına `finish_task` komutunu yapıştırır ve Graph Edge (`END`) döngüyü bitirir.

---

## 🏗️ 3. Yeni Bir Yetenek (Skill) Nasıl Eklenir?

Jarvis modern bir AI sistemi olduğu için artık yüzlerce satır *İf-Else* yazmanıza gerek yoktur. Modelin algılayıcı `schema_generator` kütüphanesi sayesinde sadece DocString yazarak modeli eğitebilirsiniz.

### Senaryo 1: Standart Lokal Bir Yetenek Eklemek (Disk/Otomaston)
Diyelim ki sistemin bataryasını ölçen `get_battery_status` aracı yazacaksınız.

#### Adım 1: Yeni Python Modülünü ve Fonksiyonunu Oluştur
`Skills/hardware_skills.py` dosyası açıp içine şunu yazın:
```python
def get_battery_status() -> str:
    \"\"\"
    Jarvis'in veya bilgisayarın mevcut pil durumunu öğren.
    Sadece donanımsal güç isteklerinde kullan.
    \"\"\"
    return "Batarya seviyesi %85 ve şarj ediliyor."
```
Önemli olan nokta: **Modeller bu docstring() yapılarını ve Args: alanlarını okuyarak** ne zaman hangi aracı tetikleyeceklerine karar verirler! Pydantic ve Type Hint kullanımını önemseyin.

#### Adım 2: Onu Dispatcher'a Tanıt (`Skills/skills_manager.py`)
`get_battery_status` aracının adını Ana Fırlatıcıya (Dispatcher) öğretin.
```python
from Skills.hardware_skills import get_battery_status

SKILL_MAP: dict[str, Callable] = {
    # Eski yetenekler...
    "get_battery_status": get_battery_status,
}
```

### 🧠 Önemli: Müzik ve Veri Temizliği (Sanitization)
Model her zaman mükemmel veri üretemez. Örneğin, "Duman Yürek çal" dediğinizde parametreyi "Yürek çal" olarak alabilir. Bunu engellemek için `Skills/music_skills.py` içinde `clean_music_query` (Regex tabanlı eylem temizleyici) fonksiyonu kullanılır. Benzer hassas yetenekler eklerken bu tür "Sanitization" filtrelerini mutlaka uygulayın.

### Senaryo 2: Harici Dinamik Modül Yükleme (Hot-Reload Plugins) - EXE Derlemeden

Eğer uygulamanızı PyInstaller ile (.exe) derlediyseniz ve tüm projeyi baştan `build` almadan yeni bir yetenek eklemek istiyorsanız **Plugins (Eklenti) Klasörünü** kullanabilirsiniz.

Uygulamanın (veya `JarvisServer.exe`'nin) bulunduğu dizinde otomatik olarak `Plugins/` adında bir klasör açılır. İçerisine istediğiniz bir Python dosyasını (`bitcoin_araci.py` gibi) kopyalayabilirsiniz. Sistem başladığında `Core/plugin_loader.py` bu kodları `importlib` ile hafızaya (Runtime) çeker ve FastMCP ağacına gömer.

**Örnek Plugin (Plugins/bitcoin_araci.py):**
```python
from MCP.tool_registry import mcp

@mcp.tool()
def get_bitcoin_price() -> str:
    """Güncel Bitcoin fiyatını anlık olarak okur. Bitcoin fiyatı sorulduğunda kullan!"""
    return "Bitcoin şu an: $96.000"
```
Jarvis'i kapatıp açtığınızda model bu aracı hemen tanıyacak ve kullanacaktır.

### Senaryo 3: Asenkron Web Ağ/Bağlantı Skilli Eklemek (FastMCP İç Çekirdek)
Sunucu üzerinden dışarı açılan web bazlı yeteneklerin `Skills` yerine `MCP (Model Context Protocol)` üzerinden kayıt edilmesi tavsiye edilir.

`MCP/tools/` dizinine girip `.py` uzatılı aracınızda `@mcp.tool()` dekoratörünü kullanmanız yeterlidir. `LangGraph` senkron-asenkron dövüşünü kendi içerisinde çözecektir.
```python
from MCP.tool_registry import mcp

@mcp.tool()
async def trigger_home_lights(state: str) -> str:
    \"\"\"
    Akıllı ev sistemindeki ışıkları açmak veya kapatmak için kullanılır.
    
    Args:
        state: "on" veya "off" durumu.
    \"\"\"
    import httpx
    # ... http istekleri ...
    return f"Işıklar {state} durumuna getirildi."
```
(Bu aşamada MCP Registry otomatik olarak `trigger_home_lights` argümanını schema tablosuna yükleyecek ve AI bunu bir eliymiş gibi kullanabilecektir.)

---

> 🎉 **Bu Dokümanı İnceleyen AI Ajanlarına (Antigravity vb.) Ciddi Uyarı:**
>
> Projedeki System State, `app.ainvoke()` veya `app.invoke()` methodlarına sıkı sıkıya bağlıdır. Async/Sync uyumlarını `Core/async_handler.py` tarafında modifiye ederken mevcut çalışan FastMCP (Tool Registry) eşzamanlı loop engelleme cache'ini (`mcp._tool_manager.list_tools()`) kesinlikle atlamayın. Hatalara (Crash) neden olur. Mümkün olduğunca mevcut LangGraph çark çarkını bozmadan `Nodes` içine küçük mantıksal müdahalelerde bulunun.

# Jarvis AI — Kullanım Kılavuzu

Jarvis, bilgisayarında ve telefonunda sana yardım eden kişisel bir AI asistanıdır.

---

## Ne Yapabilir?

| Yetenek | Örnek Komut |
|---------|-------------|
| **Sohbet** | "Merhaba Jarvis" |
| **Dosya oluşturma** | "Masaüstüne notlar klasörü aç" |
| **Dosya silme** | "İndirilenlerden rapor.txt dosyasını sil" |
| **Müzik çalma** | "Spotify'dan müzik aç" |
| **Bilgi soruları** | "Python nedir?" |
| **Plan yapma** | "Bu projeyi nasıl organize edebilirim?" |
| **Duygu analizi** | "Sıkıldım, ne yapayım?" |
| **Kod yazma** | "Fibonacci hesaplayan Python fonksiyonu yaz" |
| **Bulut dosya** | Nextcloud üzerinden dosya okuma/yazma |
| **Hafıza** | Önemli bilgileri hatırlama ve geri çağırma |

---

## Kurulum (İlk Kez)

### Gereksinimler

| Program | İndirme Linki | Ne İçin |
|---------|--------------|---------|
| **Python 3.11+** | [python.org](https://python.org) | Jarvis'in çalışması |
| **Ollama** | [ollama.com](https://ollama.com) | Yapay zeka modelleri |
| **Tailscale** | [tailscale.com](https://tailscale.com/download) | Cihazları birbirine bağlama |
| **Docker** | Ubuntu sunucuda yüklü | Qdrant, Nextcloud, n8n |

### Adım 1: AI Modellerini İndir

Komut satırını (PowerShell) aç ve sırayla çalıştır:

```powershell
ollama pull qwen2.5:3b
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:14b
ollama pull nomic-embed-text
```

> ⏱️ Bu adım internet hızına göre 10-30 dakika sürebilir.

### Adım 2: Python Paketlerini Kur

```powershell
cd c:\Users\boran\Desktop\Jarvis_Aİ
pip install -r requirements.txt
```

### Adım 3: Tailscale Kur

1. [tailscale.com/download](https://tailscale.com/download) adresinden indir
2. Kur ve hesap oluştur (Google ile giriş yapılabilir)
3. Ubuntu sunucuya da aynı hesapla Tailscale kur
4. Her iki cihaz da bağlanınca hazır

### Adım 4: Ubuntu Sunucuda Docker Servislerini Başlat

```bash
cd ~/jarvis_stack
docker compose up -d
```

---

## Jarvis'i Başlatma

### Yöntem 1: EXE ile (Önerilen — Arka Plan)

```
c:\Users\boran\Desktop\Jarvis_Aİ\dist\JarvisAI\JarvisAI.exe
```

Çift tıkla → saat yanında mavi **J** ikonu belirir → Jarvis arka planda çalışır.

**Sağ tıkla menüsü:**

| Seçenek | Ne Yapar |
|---------|----------|
| API Docs | Tarayıcıda API arayüzünü açar |
| Health Check | Sistemin sağlıklı olup olmadığını gösterir |
| Yeniden Başlat | Jarvis'i restart eder |
| Çıkış | Jarvis'i tamamen kapatır |

### Yöntem 2: PowerShell ile

```powershell
cd c:\Users\boran\Desktop\Jarvis_Aİ
python main.py --server
```

### Yöntem 3: Konsol Sohbet

```powershell
python main.py --cli
```

Doğrudan konsolda "Sen:" yazıp sohbet edersin. Çıkmak için "çıkış" yaz.

### Yöntem 4: Grafik Arayüz

```powershell
python main.py
```

---

## Telegram'dan Kullanma

> Bu bölüm için n8n workflow'u kurulmuş olmalı.

1. Telegram'da bot'unu bul (örn: `@jarvis_tuai_bot`)
2. Mesaj yaz → Jarvis yanıtlar
3. Hepsi bu kadar!

**Örnekler:**

```
Sen:    Masaüstüne yeni-proje klasörü aç
Jarvis: Oluşturdum Efendim.

Sen:    Python nedir?
Jarvis: Python, okunması kolay sözdizimi ile bilinen yüksek 
        seviyeli bir programlama dilidir Efendim...

Sen:    Keyfim yok, bir şeyler çal
Jarvis: Keyfinizi yerine getirecek bir şeyler çalıyorum Efendim.
```

---

## Sistem Kontrolü

Her şeyin çalışıp çalışmadığını kontrol etmek için:

```powershell
cd c:\Users\boran\Desktop\Jarvis_Aİ
python health_check.py
```

**Sağlıklı çıktı:**

```
  [OK] Imports       — 13/13 modül yüklendi
  [OK] Settings      — Ayarlar doğru
  [OK] Ollama        — AI modelleri erişilebilir
  [OK] Qdrant        — Hafıza veritabanı bağlı
  [OK] Nextcloud     — Bulut depolama bağlı
  [OK] n8n           — Otomasyon çalışıyor
  [OK] FastAPI       — API sunucusu hazır
  [OK] Chat          — Gerçek sohbet testi geçti

  TUMU GECTI (8/8) — Sistem tamamen hazır!
```

---

## API ile Kullanma (Geliştiriciler İçin)

Jarvis çalışırken `http://localhost:8000/docs` adresini tarayıcıda aç.
Swagger arayüzünden tüm endpoint'leri deneyebilirsin.

### Mesaj Gönder

```bash
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\": \"boran\", \"message\": \"Merhaba\", \"platform\": \"api\"}"
```

### Sağlık Kontrolü

```bash
curl http://localhost:8000/api/health
```

---

## Bilgisayar Açıldığında Otomatik Başlatma

1. `Win + R` tuşlarına bas
2. `shell:startup` yaz ve Enter'a bas
3. Açılan klasöre `dist\JarvisAI\JarvisAI.exe` dosyasının kısayolunu kopyala
4. Artık bilgisayar her açıldığında Jarvis otomatik başlar

---

## Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| "Ollama erişilemedi" | Ollama uygulamasını aç veya `ollama serve` çalıştır |
| "Qdrant erişilemedi" | Ubuntu'da `docker compose ps` ile kontrol et, çalışmıyorsa `docker compose up -d` |
| "Port 8000 kullanımda" | Önceki Jarvis'i kapat: Görev Yöneticisi → python.exe → Görevi Sonlandır |
| Telegram'dan yanıt gelmiyor | n8n workflow aktif mi? Toggle'ı kontrol et |
| Tailscale bağlantı yok | Tailscale uygulamasını aç, bağlı olduğunu kontrol et |
| EXE açılmıyor | `dist\JarvisAI\.env` dosyası var mı kontrol et |

---

## Dosya Yapısı (Meraklılar İçin)

```
Jarvis_Aİ/
├── main.py              ← Giriş noktası (--cli / --server / GUI)
├── jarvis_tray.py       ← System tray (arka plan çalışma)
├── settings.py          ← Ayarlar (IP'ler, modeller, portlar)
├── .env                 ← Gizli anahtarlar (şifreler)
├── health_check.py      ← Sistem kontrolü
├── build_exe.py         ← EXE oluşturma
│
├── Server/              ← API sunucusu
│   ├── app.py           ←   /api/chat ve /api/health
│   ├── schemas.py       ←   Veri formatları
│   └── dependencies.py  ←   Oturum yönetimi
│
├── Core/                ← İşlem merkezi
│   ├── handler.py       ←   Konsol/GUI modu
│   └── async_handler.py ←   Server modu (async)
│
├── Brain/               ← AI beyni
│   ├── router.py        ←   Mesajı sınıflandırır
│   ├── intent_engine.py ←   Komutu anlar (ne yapılacak?)
│   ├── reasoning_engine.py ← Düşünme/planlama
│   └── coding_engine.py ←   Kod yazma
│
├── Integrations/        ← Dış bağlantılar
│   ├── qdrant_memory.py ←   Uzun vadeli hafıza
│   ├── nextcloud_client.py ← Bulut dosyalar
│   └── n8n_client.py    ←   Telegram bildirimleri
│
├── MCP/                 ← AI araçları
│   └── tools/
│       ├── memory_tools.py ← Hatırla/hatırlat
│       ├── cloud_tools.py  ← Bulut dosya oku/yaz
│       └── notification_tools.py ← Mesaj gönder
│
├── Skills/              ← Yetenekler (dosya, müzik, web)
└── dist/JarvisAI/       ← EXE çıktısı
    └── JarvisAI.exe     ← Çift tıkla ve çalıştır
```

---

## Mimari: Nerede Ne Çalışır?

```
┌──────────────────────────────────────────────────────┐
│  🧠 BU BİLGİSAYAR (Windows — 100.82.212.6)          │
│                                                      │
│  ┌─────────────┐   ┌────────────┐   ┌─────────────┐ │
│  │ FastAPI      │   │ Ollama     │   │ Skills      │ │
│  │ Gateway      │──▶│ (AI Beyin) │   │ (Dosya vb.) │ │
│  │ :8000        │   │ :11434     │   │             │ │
│  └──────┬───────┘   └────────────┘   └─────────────┘ │
│         │  Kodlar + Model + Yetenekler BURDA çalışır  │
└─────────┼────────────────────────────────────────────┘
          │ Tailscale VPN (şifreli tünel)
┌─────────┼────────────────────────────────────────────┐
│  🖥️ UBUNTU SUNUCU (100.119.172.35)                   │
│         │                                             │
│  ┌──────┴───────┐  ┌───────────┐  ┌──────────────┐  │
│  │ n8n          │  │ Qdrant    │  │ Nextcloud    │  │
│  │ (Otomasyon)  │  │ (Hafıza)  │  │ (Dosyalar)   │  │
│  │ :5678        │  │ :6333     │  │ :8080        │  │
│  └──────────────┘  └───────────┘  └──────────────┘  │
│       Bu sunucu sadece VERİ SAKLAR ve İLETİR         │
└──────────────────────────────────────────────────────┘
```

### Her Bileşen Ne Yapar?

| Bileşen | Nerede | Ne Yapar | Benzetme |
|---------|--------|----------|----------|
| **Ollama** | Bu PC | AI modellerini çalıştırır, düşünür | Beyin |
| **FastAPI** | Bu PC | Dışarıdan gelen istekleri karşılar | Kapı |
| **Router** | Bu PC | Mesajı hangi modelin cevaplayacağını belirler | Yönlendirici |
| **Skills** | Bu PC | Dosya aç, müzik çal gibi eylemleri yapar | Eller |
| **n8n** | Sunucu | Telegram mesajını alır, Jarvis'e iletir | Postacı |
| **Qdrant** | Sunucu | Jarvis'in uzun vadeli hafızası | Dosya dolabı |
| **Nextcloud** | Sunucu | Bulut dosya depolama | USB bellek |
| **Tailscale** | Her ikisi | İki cihazı şifreli bağlar | Özel yol |

---

## Bir Mesajın Tam Yolculuğu

Telefondan "Masaüstüne proje klasörü aç" yazıyorsun:

```
ADIM 1 — Telefon
  📱 Telegram'da mesaj yazıyorsun

ADIM 2 — İnternet
  ☁️ Telegram sunucusu mesajı n8n'e iletiyor

ADIM 3 — n8n (Ubuntu Sunucu)
  ⚙️ n8n mesajı alıyor, Jarvis'e gönderiyor:
     → POST http://100.82.212.6:8000/api/chat

ADIM 4 — FastAPI (Bu PC)
  🌐 İsteği alıyor → işleme veriyor

ADIM 5 — Router (Bu PC)
  🧭 "Bu basit bir komut" → qwen2.5:3b seçiliyor

ADIM 6 — Ollama (Bu PC)
  🤖 Model mesajı anlıyor:
     → {"action": "create_folder", "name": "proje"}

ADIM 7 — Skills (Bu PC)
  📁 Masaüstüne "proje" klasörü oluşturuluyor

ADIM 8 — Yanıt (Ters yön)
  FastAPI → n8n → Telegram → 📱 Telefonun
  "Oluşturdum Efendim."
```

---

## Hangi AI Modeli Ne Zaman Kullanılır?

Jarvis mesajını otomatik sınıflandırır, sen bir şey belirtmezsin:

| Mesaj Tipi | Seçilen Model | Hız | Örnek |
|------------|---------------|-----|-------|
| Basit komutlar | `qwen2.5:3b` (1.9 GB) | Çok hızlı | "Klasör aç", "Dosya sil" |
| Bilgi/düşünme | `qwen2.5:7b` (4.7 GB) | Orta | "Python nedir?", "Şunu açıkla" |
| Kod yazma | `qwen2.5-coder:14b` (9 GB) | Yavaş | "Fibonacci fonksiyonu yaz" |
| Hafıza | `nomic-embed-text` (274 MB) | Anlık | Arka planda otomatik |

---

## n8n: Ne Zaman Kod Değişir, Ne Zaman Değişmez?

### Kod DEĞİŞMEZ — Sadece n8n'de Workflow Kur

| Senaryo | n8n'de Ne Yaparsın | Jarvis Kodu |
|---------|-------------------|-------------|
| Sabah 09:00'da hava durumu gönder | Schedule + API + Telegram | Değişmez |
| Yeni bir Telegram komutu ekle | Telegram Trigger + HTTP Request | Değişmez |
| E-posta gelince Telegram'a bildir | Email Trigger + Telegram | Değişmez |
| Jarvis'e herhangi yerden soru sor | HTTP Request → `:8000/api/chat` | Değişmez |

### Kod DEĞİŞİR — Yeni Yetenek Ekleme

| Senaryo | Ne Yaparsın |
|---------|-------------|
| Jarvis'e ev otomasyonu ekle | `MCP/tools/` altına yeni tool yaz |
| Yeni bir API entegrasyonu | `Integrations/` altına yeni client yaz |
| Yeni bir komut tipi | `Brain/router.py`'ye yeni kategori ekle |

---

## Kaynak Kullanımı

| Durum | CPU | RAM | Açıklama |
|-------|-----|-----|----------|
| Boşta (mesaj yok) | %0 | ~20 MB | Sadece port dinliyor |
| Basit komut (3b) | %10-30 | ~2 GB | 1-3 saniye |
| Düşünme (7b) | %20-50 | ~5 GB | 3-10 saniye |
| Kod yazma (14b) | %40-80 | ~10 GB | 10-30 saniye |

> **Mesaj gelmediğinde Jarvis neredeyse hiç kaynak harcamaz.** Sadece port dinler — bu bir web sitesinin çalışması gibi.


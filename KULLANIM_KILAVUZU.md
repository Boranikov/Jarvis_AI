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

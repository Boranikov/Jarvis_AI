# 📖 Jarvis AI — Kullanım Kılavuzu

Hoş Geldiniz! Jarvis sadece metin sorguları cevaplayan standart bir sohbet robotu (Chatbot) değildir. **Doğrudan kişisel bilgisayarınız üzerindeki donanım ile etkileşime girebilen**, dosyalarınızı yönetip inceleyebilen, kod yazabilen ve müzik kontrolebilen akıllı, bağlantılı bir dijital "Hizmetkardır". (Servant).

---

## 🟢 1. Neler Yapılabilir? (Komut Örnekleri)

| Yetenek Alanı | Nasıl Sorulur? (Örnek Komutlar) | Arka Planda Neler Oluyor? |
| :--- | :--- | :--- |
| **☕ Sohbet / Hal Hatır** | *"Nasılsın Jarvis?", "Orada mısın?"* | Sisteme yüklü olan "Selamlama" modeli ile (1 saniyenin altında) cevap verir. |
| **📁 Dosya Operasyonları** | *"Masaüstüne proje adında klasör aç", "İndirilenlerden test.txt'yi sil"* | Dosya okuma/yazma ve System Paths yetenekleri çalışır. İşletim sistemi `os` ve `shutil` ile güvenli şekilde fiziksel değişikliği uygular. |
| **🎵 Spotify (Müzik & Duygu)** | *"Tarkan çal", "Müziği durdur", "Keyfim çok yok, bana bir şeyler aç"* | API üzerinden Spotify bağlantısı onaylanır. Cümledeki duygu analiz edilip hüzünlü/hareketli parça eşleştirilir veya belirttiğiniz isim direk Cihazda oynatılır. |
| **👨‍💻 Agent Otonom Kodlama** | *"Hesap makinesi yaz", "config.py dosyasındaki şu hatayı düzelt"* | Jarvis `Coding Engine` moduna geçer. Arka planda sizden habersiz klasörlere girer, okur, gerekirse birkaç dosya oluşturup birleştirir. Tüm proje bittiğinde size haber verir. |
| **🧠 Derin Düşünme & Plan** | *"Python'ı öğrenmek için nasıl bir plan yapmalayım?", "Şu konuyu kıyasla"* | 7 Milyar parametrelik `Reasoning` modele girer. İnternet olmadan aklındaki milyarlarca veriden yola çıkarak mantıksal plan listesi döndürür. |
| **🧮 Matematik & Analiz** | *"18'in faktöriyeli nedir?", "1545 bölü 45 x 2"* | AI matematik modeline soru aktarılır. Aynı zamanda arka planda bir Python kütüphanesi (Sympy) sonucun gerçek bir hesap makinesiyle uyuşup uyuşmadığını doğrulayarak yanılma (halüsinasyon) payını ortadan kaldırır. |

---

## 🟢 2. Uygulamayı Başlatmak ve Modlar

Jarvis projesi 3 temel başlatma (Çalışma) stiline sahiptir. İhtiyacınıza göre kullanabilirsiniz:

### Mod 1: Arayüz (Masaüstü Kullanımı İçin En İyisi)
Bu mod, en şık ve kolay kullanımlı moddur. Size PyQt6 ile yazılmış gri/siyah temalı modern bir uygulama sunar. 
Ekranda Jarvis'le klasik sohbet edebilirsiniz. Geçmiş komutlarınızı hatırlar (Yukarı ok / Aşağı ok).
**Başlatmak için:**
```bash
python main.py
```
*(Eğer program (.exe) olarak build edildiyse, masaüstündeki kısa yola tıklandığında otomatik bu açılır.)*

### Mod 2: System Tray / Arka Plan Servisi (Uzaktan Çalışmak & Sürekli Açık)
Bilgisayarınızı her açtığınızda Jarvis'in arayüzünü görmek istemiyorsunuz ancak arka planda sizi dinlesin, Telegramdan ona attığınız mesaja evdeki bilgisayarda iş yapsın istiyorsunuz. Bu mod tam bunun içindir.
Pencere açılmaz. Windows saat panelinin yanında **Küçük mavi bir Jarvis İkonu (J)** belirir.
**Başlatmak için:**
```bash
python jarvis_tray.py
# Veya argüman ile
python main.py --server
```
**Tray Menüsü (Sağ Tıklama Menüsü):** İkona sağ dıkladığınızda şu menüler gelir;
* **API Docs:** Tarayıcıda (Swagger) API port kontrol arayüzünü açar.
* **Health Check:** Tarayıcıda Jarvis'in sistem sağlığını gösteren durumu açar.
* **Yeniden Başlat:** Servis arkada sıkışırsa, modeli ve bağlantıları resetler.
* **Çıkış:** Jarvis'i ve açık kalan API kapılarını tamamen kapatıp sistemi uyutur.

### Mod 3: Konsol Terminal (Geliştirici İncelemesi İçin)
Arayüz yok. Loglar ve Düşünce yapılarının ekrana yazdırıldığı klasik yazılım geliştirici ekranı modudur. Sorun çözmek için veya hızlı işlem için harikadır.
**Başlatmak için:**
```bash
python main.py --cli
```

---

## 🟢 3. Uzaktan Kullanım (Telegram, n8n, Ağ Bağlantısı)

Jarvis'in asıl güçlü boyutu **n8n otomasyonu ve Tailscale Ağı** (Sanal Yerel Ağ) yardımıyla bilgisayarınız dışına çıkabilmesidir. Jarvis `FastAPI 8000` portundan konuşur. Sistemin ana mimari iskeleti şöyledir:

> **[ Sizin Bilgisayarınız (Modellerin olduğu Yer) ]** ↔ Tailscale ↔ **[ Ubuntu Sunucu (n8n + Qdrant Hafıza) ]** ↔ İnternet ↔ **[ Telegram (Cep Telefonunuz) ]**

### Uzaktan Nasıl Kullanırsınız?

1. Dışarıdayken (Otobüste, iş yerinde) cep telefonunuzdan Telegram'ı açın. N8n üzerinden yetkilendirdiğiniz Bot hesabına bir mesaj atın (Örn: `"Masaüstüne YeniRapor.txt aç ve içine bugün iş var yaz."`).
2. Mesajınız Telegram Server ↔ n8n'e gelir. Oradaki akış(workflow), Tailscale aracılığıyla ağa bağlı açık bilgisayarınıza (Jarvis'e) bu mesajı TCP protokolüyle fırlatır.
3. Jarvis bilgisayarınızda bir `Coding Engine` yürütür, bahsi geçen dosyayı masaüstünüze oluşturur ve kodları yazar.
4. "Masaüstünüzde rapor dosyası hazırlandı Efendim" mesajı yine aynı akış yönünde (FastAPI → n8n → Telegram) cep telefonunuza saniyeler içinde geri düşer.

Siz aslında cebinizden evdeki bilgisayarınızı, yapay zeka aklıyla kullanmış olursunuz!

> *Not: Bu yapının kurulması için `N8N_WEBHOOK_URL` ve güvenli bir Docker Compose yığınının uzak Ubuntu/VPS makinenizde kurulu olması gereklidir.*

---

## 🟢 4. Sorun Çözme & Durum Kontrolü (Hata Gidermeler)

Zamanla Ollama takılabilir, Qdrant kapanabilir veya Spotify erişimi kopabilir. Jarvis sistemin bozuk yerini kendi kontrol edebilir:

Konsola gidip yazın:
```bash
python health_check.py
```
Size detaylı bir döküm sunacaktır.

**Sık Karşılaşılan Sorunlar ve Çözümleri:**

- **HATA: "LLM bağlantısı yok" veya "Ollama Timeout" :** Ollama servisi donmuş veya model indirilmemiş olabilir. Konsoldan Ollama'nın çalıştığından emin olun (Masaüstü uygulamasını açın). RAM'iniz dolmuş olabilir.
- **HATA: Model çok mantıksız şeyler yazıyor / Çöküyor:** Bazen sistem modeli hafızadan yanlış atabilir. `jarvis_tray.py` kullanıyorsanız sağ alttaki ikona sağ tıklayıp "Yeniden Başlat" diyerek servisi tazeleyebilirsiniz.
- **HATA: n8n üzerinden Telegram mesajım bilgisayarımdaki Jarvis'e ulaşmıyor :** Tailscale VPN bağlantınızı kontrol edin. Muhtemelen Ubuntu VPS sunucunuz bilgisayarınıza Tailscale IP'si 100.x.x.x üzerinden "Ping" atamıyordur. Bilgisayarınızdaki Tailscale uygulamasını aç kapa yapın. Port `8000` başka bir app tarafından işgal edilmiş mi bakın.

---

> 🎉 **Jarvis'i geliştirmek, kod katarak yeni komutlar ekletmek veya Mimarisine göz atmak isterseniz; `DEVELOPER_GUIDE.md` dosyasına bakmalısınız.**

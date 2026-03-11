# 📖 Jarvis AI — Kullanım Kılavuzu

Hoş Geldiniz! Jarvis sadece metin sorguları cevaplayan standart bir sohbet robotu (Chatbot) değildir. **Doğrudan kişisel bilgisayarınız üzerindeki donanım ile etkileşime girebilen**, dosyalarınızı yönetip inceleyebilen, kod yazabilen ve müzik kontrol edebilen akıllı, bağlantılı bir dijital "Hizmetkardır" (Servant).

---

## 🟢 1. Neler Yapılabilir? (Komut Örnekleri)

Sistem `Qwen3:1.7b` altyapısı ve **Otonom Ajan (Agentic Tool Calling)** teknolojisiyle donatıldığı için ne yapması gerektiğine saniyenin onda biri hızında kendisi karar verir.

| Yetenek Alanı | Nasıl Sorulur? (Örnek Komutlar) | Arka Planda Neler Oluyor? |
| :--- | :--- | :--- |
| **☕ Sohbet / Hal Hatır** | *"Nasılsın Jarvis?", "Orada mısın?"* | Sisteme yüklü olan "Selamlama" modülü ile (1 saniyenin altında) doğrudan cevap verir. |
| **📁 Dosya Operasyonları** | *"Masaüstüne proje adında klasör aç", "İndirilenlerden test.txt'yi sil"* | Dosya okuma/yazma yetenekleri çalışır. İşletim sistemi `os` ve `shutil` ile güvenli şekilde fiziksel değişikliği uygular. |
| **🧠 Qdrant Vektör Hafıza (Hatırlama)** | *"Sana geçen hafta anlattığım proje fikrindeki şirket adımı bana hatırlat."* | Söyledikleriniz RAG (Retrieval-Augmented Generation) havuzundan çekilir. Ajan arama aracını otonom kullanarak size geçmiş bağlamı söyler. |
| **🎵 Spotify (Müzik & Duygu)** | *"Tarkan Öp çal", "Duman Yürek aç", "Keyfim çok yok, bana bir şeyler aç"* | API üzerinden Spotify bağlantısı onaylanır. Sanatçı ve şarkı otomatik ayrıştırılır, gereksiz kelimeler (çal, aç vb.) temizlenir ve nokta atışı arama yapılır. |
| **👨‍💻 Agent Otonom Kodlama** | *"Hesap makinesi yaz", "Şu dizindeki projeye girip X hatasını düzelt"* | Jarvis `Coding Engine` moduna geçer. Arka planda sizden habersiz klasörlere girer, okur, gerekirse birkaç dosya oluşturup birleştirir. Tüm proje bittiğinde size haber verir. |

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
*(Eğer program (.exe) olarak derlendiyse, masaüstündeki kısa yola tıklandığında otomatik bu açılır.)*

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
* **API Docs:** Tarayıcıda FastAPI (Swagger) port kontrol arayüzünü açar.
* **Health Check:** Tarayıcıda Jarvis'in sistem sağlığını (Ollama, Nextcloud, Qdrant durumu) gösteren modülü açar.
* **Yeniden Başlat:** Servis arkada sıkışırsa, modeli ve bağlantı çarkını tazeleyerek güvence altına alır.
* **Çıkış:** Jarvis'i ve açık kalan API kapılarını tamamen kapatıp sistemi uyutur.

### Mod 3: Konsol Terminal (Geliştirici İncelemesi İçin)
Arayüz yok. LangGraph düğüm geçişlerinin (Düşünce yapılarının) şeffaf bir şekilde ekrana yazdırıldığı yazılım geliştirici ekranı modudur. Sorun çözmek için veya otonom sistemleri izlemek harikadır.
**Başlatmak için:**
```bash
python main.py --cli
# veya sistem yoluna eklediyseniz:
jarvis
```
**Özel Komutlar:**
* `/debug on`: Detaylı logları (LangGraph geçişleri, API istekleri) açar.
* `/debug off`: Sadece kritik hataları gösteren temiz moda geçer.
* `/debug clear`: (Eğer terminal destekliyorsa) Ekranı temizler.
* `/debug exit`: Uygulamadan çıkar.

---

## 🟢 3. Uzaktan Kullanım (Telegram, n8n, Ağ Bağlantısı)

Jarvis'in asıl güçlü boyutu, **FastMCP** mimarisi üzerinden harici protokolleri içeri alması ve **n8n otomasyonu ve Tailscale Ağı** (Sanal Yerel Ağ) yardımıyla bilgisayarınız dışına çıkabilmesidir. Ayrıca `jarvis.bat` dosyası ile sistemin her yerinden hızlıca başlatılabilir. Jarvis `FastAPI 8000` portundan konuşur. Sistemin ana mimari iskeleti şöyledir:

> **[ Sizin Bilgisayarınız (Modellerin / Qwen3'ün olduğu Yer) ]** ↔ Tailscale ↔ **[ Ubuntu Sunucu (n8n + Qdrant Hafıza + Nextcloud) ]** ↔ İnternet ↔ **[ Telegram (Cep Telefonunuz) ]**

### Uzaktan Nasıl Kullanırsınız?

1. Dışarıdayken (Otobüste, iş yerinde) cep telefonunuzdan Telegram'ı açın. N8n üzerinden yetkilendirdiğiniz Bot hesabına bir mesaj atın (Örn: *"Evdeki bilgisayarımın masaüstüne Alınacaklar.txt aç ve içine süt yaz."*).
2. Mesajınız Telegram Server ↔ n8n'e gelir. Oradaki akış(workflow), Tailscale aracılığıyla ağa bağlı açık bilgisayarınıza (Jarvis'e) bu mesajı asenkron olarak fırlatır.
3. Jarvis bilgisayarında `Agent Node` bunu otonom düşünür, bahsi geçen dosyayı masaüstünüze oluşturur.
4. "Masaüstünüzde Alınacaklar dosyası hazırlandı Efendim" mesajı yine aynı akış yönünde (FastAPI → n8n → Telegram) cep telefonunuza saniyeler içinde (Ollama GPU hızınıza oranla) geri düşer.

Siz aslında cebinizden evdeki bilgisayarınızı, yapay zeka aklıyla kullanmış olursunuz!

> *Not: Bu yapının kurulması için `JARVIS_N8N_WEBHOOK_URL` ve güvenli bir Docker Compose yığınının uzak Ubuntu/VPS makinenizde kurulu olması gereklidir.*

---

## 🟢 4. Sorun Çözme & Durum Kontrolü (Hata Gidermeler)

Zamanla Ollama takılabilir, Qdrant kapanabilir veya Nextcloud/Spotify erişimi kopabilir. Jarvis sistemin bozuk yerini kendi kontrol edebilir:

Konsola gidip yazın:
```bash
python health_check.py
```
Size detaylı bir döküm sunacaktır.

**Sık Karşılaşılan Sorunlar ve Çözümleri:**

- **HATA: "LLM bağlantısı yok" veya "Ollama Timeout" :** Ollama servisi donmuş veya `qwen3:1.7b` modeli indirilmemiş olabilir. Konsoldan Ollama'nın çalıştığından emin olun (Masaüstü uygulamasını açın veya `ollama run qwen3:1.7b` testi yapın).
- **HATA: Model takılı kaldı / Sunucu kilitlendi:** Proje ReAct Node mimarisinde çalışır, eğer donanımınız aşırı yüklendiyse Node grafikten çıkamayabilir. `jarvis_tray.py` kullanıyorsanız sağ alttaki ikona sağ tıklayıp "Yeniden Başlat" diyerek servisi veya sunucuyu Ctrl+C ile kapatıp tekrar açabilirsiniz.
- **HATA: n8n üzerinden Telegram mesajım bilgisayarımdaki Jarvis'e ulaşmıyor :** Tailscale VPN bağlantınızı kontrol edin. Muhtemelen Ubuntu sunucunuz bilgisayarınıza IP (100.x.x.x) üzerinden "Ping" atamıyordur. Bilgisayarınızdaki Tailscale uygulamasını aç kapa yapın. Port `8000` başka bir süreç tarafından işgal edilmiş mi bakın.

---

> 🎉 **Jarvis'i geliştirmek, yeni ajan yetenekleri (Tool) ekletmek veya Mimarisine göz atmak isterseniz; `DEVELOPER_GUIDE.md` dosyasına bakmalısınız.**

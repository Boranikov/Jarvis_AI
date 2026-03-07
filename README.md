# 🤖 Jarvis AI — Akıllı Kişisel Asistan

Jarvis, yerel bilgisayarınız üzerinde (Tailscale ve Ollama aracılığıyla) tamamen size özel ve **ağ bağlantılı cihazlarla konuşabilen** hibrit bir Yapay Zeka kişisel asistan projesisidir. Windows sisteminde bir UI (kullanıcı arayüzü), komut satırı veya System Tray üzerinde arka plan servisi gibi çalışabilir. Aynı zamanda, n8n üzerinden Telegram veya Web tarayıcınıza bağlanarak dış dünyadan (FastAPI) da istek alır.

> **3 Ayrı AI Modeli** · **Otonom Kod (Agentic) Yazma** · **Spotify / Bulut (Nextcloud) Entegrasyonu** · **Sağlam API Altyapısı**

---

## 🎯 Proje Özeti: Jarvis Neler Yapabilir?

Asistan basit sohbetlerin ötesinde bilgisayarınızda fiziksel veya dosya bazlı eylemleri kendi başına yürütebilir. Temel yetenekleri şunlardır:

1. **Dosya & Klasör Yönetimi:** Seçilen dizinde dosyalar oluşturma, okuma, ağaç yapısını analiz etme ve hatta dosyaları silme.
2. **Müzik ve Medya Kontrolü:** Spotify ile tam entegre çalışır. Ruh halinize göre şarkı aratabilir, listelere ulaşabilir, çalma/durdurma başlatabilirsiniz.
3. **Agentic Kodlama:** Sadece kod önermekle kalmaz; `write_to_file`, `list_dir_recursive` araçlarıyla birlikte bir projeyi (örn. hesap makinesi) bir disk ortamına **tam çalışan koduyla ve klasör mimarisiyle** kendi yazar. Hataları bulup refactor(düzenleme) edebilir.
4. **Kişisel Hafıza (Qdrant):** Yapılan sohbetlerdeki bağlamı anlar ve bunu bir Vektör Veritabanı içinde vektörel kelimeler (embeddings) olarak tutar. Aylar sonra sorduğunuz bir konuyu anımsayarak sohbete dahil eder.
5. **Duygu Analizi:** Kurduğunuz cümlelerin olumlu/olumsuz duygu durumunu çıkarır, empatik yanıt verir veya sizi eğlendirmek için otomatik şarkı önerilerde bulunur.
6. **Telegram & Bulut Erişilebilirliği:** Evde çalışan Jarvis'e cep telefonunuzdan Telegram vasıtasıyla kod yazdırabilir, sunucu (Nextcloud) üzerindeki dökümanlarınıza müdahale edebilirsiniz.

---

## 🏗️ Modüler Mimari (Tek Bakışta Yapı)

Jarvis'in kodu gelişmiş bir **"Intent (Niyet) Yönlendirme"** sistemine dayanır. Sistem, kullanıcının "Ne İstediğini" tek bir ana dilde anlamaya odaklanır ve sonuca göre uygun aracı ya da AI Modelini ateşler. `Qwen2.5` Local LLM grubunun 3 farklı versiyonunu projenin beynine yerleştirilmiştir:

### `Brain/` (AI'ın Beyni)
- `router.py`: İstek ilk buraya girer. İçindeki keyword, regex ve duygu analizi mekanizmalarıyla hızlıca isteğin basit bir skill (eylem) mi, plan (reasoning) mı yoksa otonom bir kod (coding) mu olacağını tespit eder. Bazen matematik denklemi gibi net mantık yapılarını ayrıştırır.
- `intent_engine.py`: **(Hızlı düşünme modeli - qwen2.5:3b)**. En ufak LLM modelidir. Amacı saniyeden kısa sürede JSON formatında aksiyon objesi (`create_folder`, `play_music` vs.) ve argümanları (Parametreler: `{"path":"desktop", "name":"test"}`) döner.
- `reasoning_engine.py`: **(Derin düşünme modeli - qwen2.5:7b)**. Soyut istekleri, empati durumunu, genel dünya bilgisini veya çok aşamalı (plan yapılarak ilerlenecek) komutları parçalamak için kullanılır. Planların yürütülebilir çıktılarını liste halinde döndürür.
- `coding_engine.py`: **(Kodlama modeli - qwen2.5-coder:14b)**. Tam otonomdur (Agentic loop). Sistemi bozana kadar veya kendi hedefine ulaşana kadar (Maksimum iterasyon = 15) defalarca dosya okuma, dosya yazma işlemleri yapar. Tam çalışmayan veya "pass" ile bırakılmış kodları onaylamaz.
- `memory.py` / `plan_executor.py`: Kısa vadeli sohbet dizilerini ve eksik parametreleri tutar, Reasoning'den çıkan sıralı planları sırayla yürütür.

### `Core/` & `Server/` (Kasa ve Kapı)
- `Core/handler.py`: Bütün mantık yollarını birleştiren merkezdir. Komut neyse (CLI veya GUI tabanlı), gerekli modülü tetikler, eksik durum varsa hafızaya pending parametre düşerek soruyu kullanıcıya iade eder. Matematik doğrulayıcı çalıştırır.
- `Server/app.py`: Jarvis, sadece PC arayüzünde değil arka planda bir **FastAPI** sunucusu olarak çalışır. `http://0.0.0.0:8000` portundan açılan uç ile Telegram (n8n Webhook) üzerinden bağlanan mesajları Server içinde izole eder, `async_handler.py` ile asenkron şekilde çözer. 
- `Server/dependencies.py`: FastAPI State ve Context paylaşımlarını, Qdrant/Ollama/Nextcloud/Spotify bağlantı check'lerini (Lifespan Lifecycle) organize eder.

### `Skills/` & `Integrations/` & `MCP/` (Eller ve Ayaklar)
- `Skills/`: Modelin kullanabildiği fiziksel işlevlerdir. `file_skills.py` dosyası cihazdaki gerçek I/O (Girdi/Çıktı) okuma-yazmalarını, `music_skills.py` ise Spotipy kütüphanesi ile şarkı kontrollerini halleder. Tüm yönlendirmeler `skills_manager.py` (Dispatcher) ile tek noktadan fırlatılır.
- `MCP/` ve `Integrations/`: Dış dünyadaki Vektör veritabanına, Tailscale tünellerine ve bulut deposuna ait yardımcı fonksiyon ve modüller klasörleridir. (Model Context Protocol).

---

## 🚀 Başlamadan Önce (Kurulum)

Sistemi denemek veya kendi ortamınızda kurmak için:

### 1. Python Gereksinimleri
Python 3.11+ kullandığınızdan emin olun. Terminalden çalıştırın:
```bash
pip install -r requirements.txt
```

### 2. Yapay Zeka (Ollama) Modellerinin İndirilmesi
Jarvis gücünü Ollama üzerinden çalıştırılan model setlerinden alır.
Aşağıdaki modelleri bilgisayarınıza indirin (RAM'iniz en az 16GB, tercihen 32GB olmalıdır):
```bash
ollama pull qwen2.5:3b           # Hızlı araç tespit modeli
ollama pull qwen2.5:7b           # Düşünme ve Planlama modeli
ollama pull qwen2.5-coder:14b    # Kodlama modeli
ollama pull nomic-embed-text     # Hafıza Embedding (Metni vektöre çeviren dil)
```

### 3. API Anahtarları (.env Yapılandırması)
Ana dizindeki veya `dist/JarvisAI` klasöründeki `.env` dosyasını yapılandırın:
```env
# Spotify Bilgileriniz
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

# (Eğer kurulduysa) Diğer Entegrasyonlar
N8N_WEBHOOK_URL=http://.../webhook/jarvis
QDRANT_API_KEY=...
```

### 4. Çalıştırma
Jarvis 3 modda çalışabilir. Kullanacağınız amaca göre uygun komutu seçin:

**Mod 1: Arayüz (GUI)**
Hızlı, gri-siyah tonlarda şık, modern bir sohbet baloncuğu deneyimi sunar:
```bash
python main.py
```

**Mod 2: Konsol (CLI)**
Sadece terminal üzerinden, en hafif ve log detayları açık çalışan moddur:
```bash
python main.py --cli
```

**Mod 3: Sunucu Modu (Background Tray & Dağıtık)**
Bu modda GUI açılmaz, ekranın sağ altına sadece bir J logolu System Tray ikonu oturur. Arka planda FastAPI sunucusu aktifleşir ve Tailscale / Telegram / Web üzerinden kullanıma hazır port dinler.
```bash
python jarvis_tray.py
# veya
python main.py --server
```

### 5. Sistemin Sağlığını Kontrol Etmek
Tüm mikroservislerin (Qdrant, Ollama, FastAPI) bağlantısını test eden yardımcı aracı çalıştırın:
```bash
python health_check.py
```

---

Daha fazla yapılandırma, System Tray kullanımları, n8n-Telegram entegrasyonu hakkında bilgi için lütfen **[KULLANIM_KILAVUZU.md](KULLANIM_KILAVUZU.md)** dosyasını okuyun. Mimariye müdahale edecek ve yeni özellik (Yetenekler veya Skill) katacak geliştiriciler/Mimar AI Modelleri için mutlaka **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** belge rehberini incelemelidir!

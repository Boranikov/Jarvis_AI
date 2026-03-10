# 🤖 Jarvis AI — Akıllı Kişisel Asistan (ReAct Agent Mimarisi)

Jarvis, yerel bilgisayarınız üzerinde (Tailscale ve Ollama aracılığıyla) tamamen size özel ve **ağ bağlantılı cihazlarla konuşabilen** hibrit bir Yapay Zeka kişisel asistan projesidir. Windows sisteminde bir UI (kullanıcı arayüzü), komut satırı veya System Tray üzerinde arka plan servisi gibi çalışabilir. Aynı zamanda, n8n üzerinden Telegram veya Web tarayıcınıza bağlanarak dış dünyadan (FastAPI) da istek alır.

> **LangGraph ReAct Mimarisi** · **Otonom Kod (Agentic) Yazma** · **Qdrant Vektör Hafıza (RAG)** · **FastMCP Tool Sistemi**

---

## 🎯 Proje Özeti: Jarvis Neler Yapabilir?

Asistan basit sohbetlerin ötesinde bilgisayarınızda fiziksel veya dosya bazlı eylemleri kendi başına yürütebilir. Temel yetenekleri şunlardır:

1. **Dosya & Klasör Yönetimi:** Seçilen dizinde dosyalar oluşturma, okuma, ağaç yapısını analiz etme ve hatta dosyaları silme.
2. **Müzik ve Medya Kontrolü:** Spotify ile tam entegre çalışır. Ruh halinize göre şarkı aratabilir, listelere ulaşabilir, çalma/durdurma başlatabilirsiniz.
3. **Agentic Kodlama:** Sadece kod önermekle kalmaz; `write_to_file`, `list_dir_recursive` araçlarıyla birlikte bir projeyi (örn. hesap makinesi) bir disk ortamına **tam çalışan koduyla ve klasör mimarisiyle** kendi yazar. Hataları bulup refactor(düzenleme) edebilir.
4. **Kişisel Hafıza (Qdrant & RAG):** Yapılan sohbetlerdeki bağlamı anlar ve bunu bir Vektör Veritabanı içinde (Embeddings) tutar. Aylar sonra sorduğunuz bir konuyu (Örn: "Daha önce adımın ne olduğundan bahsettiğimiz konuşmayı bul") anımsayarak sohbete dahil eder.
5. **Duygu Analizi:** Kurduğunuz cümlelerin olumlu/olumsuz duygu durumunu çıkarır, empatik yanıt verir veya sizi eğlendirmek için otomatik şarkı önerilerde bulunur.
6. **Telegram & Bulut Erişilebilirliği:** Evde çalışan Jarvis'e cep telefonunuzdan Telegram vasıtasıyla kod yazdırabilir, sunucu (Nextcloud) üzerindeki dokümanlarınıza MCP protokolüyle asenkron şekilde müdahale edebilirsiniz.

---

## 🏗️ Modüler Mimari (Tek Bakışta Yapı)

Jarvis'in güncel sürümü **ReAct (Reasoning and Acting)** konseptiyle `LangGraph` altyapısı üzerine kurulmuştur. `Qwen3:1.7b` gibi süper hızlı veya `Qwen2.5-Coder:14b` gibi kodlama odaklı modellerle entegredir. Model, tek bir "Girdi" üzerinden anında aletleri (Tools/Skills) kullanıp kullanamayacağına kendi otonom karar verir.

### `Brain/` (AI'ın Beyni - LangGraph)
- `graph_router.py`: İsteklerin asenkron olarak aktığı, StateGraph düğümlerinin tutulduğu asıl orkestra şefidir.
- `graph_nodes.py`: `agent_node` ve `tool_node` yapılarını barındırır. Model (Qwen3) düşünür (Think), araç kullanmaya karar verirse (Action), işlem `tool_node`'a kayar (Observation) ve tekrar `agent_node`'a döner. Hedef başarılı olduğunda işlemi `finish_task` aracıyla sonlandırır.
- `coding_engine.py`: **(Kodlama Modeli - qwen2.5-coder:14b)**. Tam otonomdur (Agentic loop). Sistemi bozana kadar veya kendi hedefine ulaşana kadar (Maksimum iterasyon = 15) defalarca dosya okuma, dosya yazma işlemleri yapar. Tam çalışmayan kodları onaylamaz.
- `memory.py`: Kısa vadeli sohbet dizilerini ve çok turlu diyalog bağlamlarını tutar.

### `Core/` & `Server/` (Kasa ve Kapı)
- `Core/handler.py`: Senkron çalışan arayüz (GUI ve CLI) kullanıcılarının isteklerini LangGraph Ajanına aktaran ana işleyicidir. "Jarvis orda mısın" gibi varlık kontrollerini anında yanıtlar.
- `Core/async_handler.py`: Asenkron çalışan FastAPI (Sunucu) uçlarının isteklerini, eşzamanlı kopmalar yaşatmaksızın doğrudan `graph_router.py` motoruna enjekte eder.
- `Server/app.py`: Jarvis, sadece PC arayüzünde değil arka planda bir **FastAPI** sunucusu olarak çalışır. `http://0.0.0.0:8000` portundan açılan uç ile Telegram (n8n Webhook) üzerinden bağlanan iletileri (Payload) karşılar.

### `Skills/` & `MCP/` (Eller ve Ayaklar)
- `Skills/`: Modelin kullanabildiği fiziksel işlevlerdir. `file_skills.py` cihazdaki gerçek okuma-yazmaları, `music_skills.py` ise Spotify API kontrollerini (Keskin arama ve sanitizasyon ile) halleder. Tüm lokal yetenekler ve schema dönüşümleri `skills_manager.py` ile tek noktadan fırlatılır.
- `MCP/` (Model Context Protocol): FastMCP altyapısıyla harici uçları (Nextcloud, Qdrant RAG, Bildirim sistemleri) LLM'in anlayacağı "Tool" dizilerine standartlaştırır. Ağ üzerinden gelen bu asenkron yapı `tool_registry.py` yardımıyla senkron bir şekilde LangGraph sarmalına bağlanır.

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
ollama pull qwen3:1.7b           # Hızlı otonom ajans modeli (ReAct)
ollama pull qwen2.5:7b           # Ağır muhakeme modeli
ollama pull qwen2.5-coder:14b    # Kodlama otonom modeli
ollama pull nomic-embed-text     # Hafıza Embedding (Metni vektöre çeviren RAG modeli)
```

### 3. API Anahtarları (.env Yapılandırması)
Ana dizindeki veya `dist/JarvisAI` klasöründeki `.env` dosyasını yapılandırın:
```env
# Spotify Bilgileriniz
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback

# (Eğer kurulduysa) Diğer Entegrasyonlar
JARVIS_N8N_WEBHOOK_URL=http://.../webhook/jarvis
JARVIS_QDRANT_URL=http://...:6333
```

### 4. Çalıştırma
Jarvis 3 modda çalışabilir. Kullanacağınız amaca göre uygun komutu seçin:

**Mod 1: Arayüz (GUI)**
Hızlı, gri-siyah tonlarda şık, modern bir sohbet baloncuğu deneyimi sunar:
```bash
python main.py
```

**Mod 2: Konsol (CLI) - Önerilen**
Modern, büyük fontlu bir açılış ekranıyla başlar. Log detayları `/debug` komutlarıyla kontrol edilebilir:
```bash
python main.py --cli
# veya
jarvis.bat
```

**Mod 3: Sunucu Modu (Background Tray & Dağıtık)**
Bu modda GUI açılmaz, ekranın sağ altına sadece bir J logolu System Tray ikonu oturur. Arka planda FastAPI sunucusu aktifleşir ve Tailscale / Telegram / Web üzerinden kullanıma hazır port dinler.
```bash
python jarvis_tray.py
# veya
python main.py --server
```

### 5. Sintemi Test Etmek
Tüm mikroservislerin (Qdrant, Ollama, FastAPI) bağlantısını test eden yardımcı aracı çalıştırın:
```bash
python health_check.py
```

---

Daha fazla yapılandırma, System Tray kullanımları, n8n-Telegram entegrasyonu hakkında bilgi için lütfen **[KULLANIM_KILAVUZU.md](KULLANIM_KILAVUZU.md)** dosyasını okuyun. Mimariye müdahale edecek ve yeni özellik (Yetenekler veya Skill) katacak geliştiriciler/Mimar AI Modelleri için mutlaka **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** belge rehberini incelemelidir!

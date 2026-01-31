# 🎓 Jarvis Projesi - BAŞTAN SONA REHBER

**Bu rehber hiç GitHub kullanmamış birisine projeyi ve workflow'u anlatır.**

---

## 📍 İçindekiler

1. [Proje Mimarisi](#proje-mimarisi)
2. [Dosya Yapısı ve Açıklaması](#dosya-yapısı-ve-açıklaması)
3. [Kod Akışı (Flow)](#kod-akışı-flow)
4. [Hangi Kod Nereye Yazılır](#hangi-kod-nereye-yazılır)
5. [Git ve Branch Rehberi](#git-ve-branch-rehberi)
6. [Başlangıç - Adım Adım](#başlangıç---adım-adım)

---

## 1️⃣ Proje Mimarisi

Bu proje **Türkçe konuşan AI asistanı**. Nasıl çalışır:

```
┌─────────────────────────────────────────────────────────────────┐
│                     KULLANICIYı GİRDİ                           │
│        "Jarvis, test.txt oluştur" (Terminal'de yazıyor)        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  main.py    │ ← Ana program
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼─────┐      ┌────▼─────┐     ┌────▼─────┐
    │ Intent   │      │ Memory   │     │ Utils   │
    │ Engine   │      │ Management     │ Helpers │
    │ (brain)  │      │ (brain)  │     │         │
    └────┬─────┘      └────┬─────┘     └────┬─────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────────┐
                    │ Skills Manager  │ ← Aksiyonları yap
                    │ (Dosya oluştur)│
                    └─────────────────┘
                           │
                    ┌──────▼──────┐
                    │    SONUÇ    │
                    │ ✓ Dosya    │
                    │ oluşturuldu│
                    └─────────────┘
```

---

## 2️⃣ Dosya Yapısı ve Açıklaması

### 📁 Klasör ve Dosya Haritası

```
Jarvis_Aİ/                          ← Proje ana klasörü
│
├── 📄 main.py                      ← ⭐ BAŞLANGIÇ NOKTASI (Programa git)
│                                      Ana program döngüsü
│
├── 📄 config.py                    ← ⚙️ AYARLAR
│                                      - Komutlar (keywords)
│                                      - Sorulan sorular
│                                      - LLM modeli seçimi
│
├── 📄 utils.py                     ← 🛠️ YARDIMCI ARAÇLAR
│                                      - Text işleme
│                                      - Name çıkartma
│                                      - Debug yazma
│
├── 📁 brain/                       ← 🧠 AKIL (NLP ve hafıza)
│   ├── __init__.py                 (Python modülü olarak tanıtmak için)
│   ├── intent_engine.py            ← Metin analizi (LLM ile)
│   └── memory.py                   ← Konuşma hafızası
│
├── 📁 Skills/                      ← 🎯 AKSIYONLAR (Gerçek işlemler)
│   ├── __init__.py                 (Python modülü olarak tanıtmak için)
│   └── skills_manager.py           ← Dosya oluştur, müzik çal, vb.
│
├── 📁 .github/                     ← GitHub Yapılandırması
│   ├── pull_request_template.md    (PR formu)
│   └── ISSUE_TEMPLATE/             (Bug ve feature formları)
│
├── 📄 README.md                    ← 📖 Proje açıklaması
├── 📄 CONTRIBUTING.md              ← Nasıl katkı yaparsın
├── 📄 BRANCHING_STRATEGY.md        ← Git branch kuralları
├── 📄 GIT_STRUCTURE_SUMMARY.md     ← Git yapısı
├── 📄 requirements.txt              ← Python kütüphaneleri (pip install)
└── 📄 setup.py                     ← Kurulum betiği
```

---

## 3️⃣ Kod Akışı (Flow)

### 🔄 Kullanıcı "Jarvis, test.txt oluştur" Dediğinde Ne Olur?

```
ADIM 1: INPUT ALINI
────────────────────
main.py → input("Sen: ") 
          ↓
          "jarvis, test.txt oluştur"


ADIM 2: KONTROL EDILIR
────────────────────
main.py → Sistem modu mu? (presence check)
        → "jarvis orada mısın?" ise cevap ver
        → Bekleyen işlem var mı? (hafızada kaydedilmiş eksik param)
        ↓
        ÖKK, normal işlem


ADIM 3: NLP ANALİZİ (ANLAMA)
────────────────────────────
main.py → brain/intent_engine.py
          ↓
          Ollama LLM'e gönder:
          - System prompt: Türkçe, JSON, action'lar nedir?
          - User input: "test.txt oluştur"
          ↓
          LLM döndürür:
          {
            "action": "create_file",
            "reply": "test.txt dosyası oluşturuyorum",
            "name": "test.txt",
            "parameters": {}
          }


ADIM 4: PARAMETRELERI AYARLA
─────────────────────────────
main.py → config.py'yi kontrol et
        → utils.py → extract_name_from_input() çağrı
        → Eksik param var mı? (name, path, vb.)
        ↓
        Params dolduruldu:
        {
          "name": "test.txt",
          "path": "desktop"
        }


ADIM 5: AKSİYONU ÇALIŞTIR
──────────────────────────
main.py → Skills/skills_manager.py
          ↓
          perform_skill(action="create_file", params={...})
          ↓
          Dosya sistemi işlemi:
          - C:\Users\boran\Desktop\test.txt oluştur
          ↓
          ">> [OK] Dosya oluşturuldu: C:\Users\boran\Desktop\test.txt"


ADIM 6: HAFIZAYA KAYDET
────────────────────────
main.py → brain/memory.py
        → memory.add(user_input, reply)
        ↓
        Son 10 konuşma kaydedildi (später AI training için)
```

---

## 4️⃣ Hangi Kod Nereye Yazılır?

### 📊 KOD TÜRLERİ TABLOSU

| Kod Türü | Nereye? | Dosya | Örnek |
|----------|---------|-------|--------|
| **YENİ KOMUT EKLEMEK** | `config.py` | `ACTION_KEYWORDS` | `"send_email": ["gönder", "e-mail"]` |
| **SORU EKLEMEK** | `config.py` | `MISSING_QUESTIONS` | `"send_email": {"to": "Kime göndermek istiyorsun?"}` |
| **LLM SYSTEM PROMPT** | `brain/intent_engine.py` | `SYSTEM_PROMPT` | Yeni action tipi türü eklemek |
| **METIN İŞLEME** | `utils.py` | `extract_name_from_input()` | Yeni keyword temizleme |
| **HAFIZA GEREKLİ** | `brain/memory.py` | `Memory` class | Session state tutmak |
| **DOSYA/MÜZİK İŞLEMİ** | `Skills/skills_manager.py` | `perform_skill()` | Yeni aksiyon (printer kullan, vb.) |
| **AYARLAR/SABITLER** | `config.py` | Top level | `LLM_MODEL = "gemma2:2b"` |
| **DEBUG/LOGGING** | `utils.py` | `debug_print()` | Hata ayıklama mesajları |
| **TEST** | `tests/` (yeni oluştur) | `test_*.py` | Unit test'ler |

### 📝 DOSYA DETAYLARı

#### 🎯 **main.py** - ANA PROGRAM
```
main.py ne yapar?
├─ Programı başlat (while True loop)
├─ Kullanıcı inputu al
├─ Intent engine'e gönder
├─ Parametreleri kontrol et
├─ Skills manager'ı çağır
├─ Sonucu göster
└─ Hafızaya kaydet

Ne YAZARSIN burada?
- Yeni command flow'u (örn. admin paneli)
- Yeni UI element'ler (örn. menu)
- Global error handling
```

#### ⚙️ **config.py** - AYARLAR
```
config.py ne tutar?
├─ ACTION_KEYWORDS = {...}      ← Komut trigger kelimeleri
├─ REQUIRED_PARAMS = {...}      ← Her action için gerekli parametreler
├─ MISSING_QUESTIONS = {...}    ← Eksik param sorularından
├─ LLM_MODEL = "gemma2:2b"       ← Kullanılan model
└─ ATTENTION_WORDS = [...]      ← Kaldırılacak kelimeler

Ne YAZARSIN burada?
- Yeni action keyword'ü
- Yeni soru metni
- LLM parametreleri (temperature, vb.)
```

#### 🧠 **brain/intent_engine.py** - AKIL
```
intent_engine.py ne yapar?
├─ Ollama LLM'e metin gönder
├─ LLM'den JSON yanıt al
├─ JSON'ı parse et
├─ Yanıta "Efendim" ekle
└─ main.py'ye döndür

Ne YAZARSIN burada?
- SYSTEM_PROMPT güncelleme (yeni action tipi)
- LLM yanıtını işleme (parse, validation)
- Error handling (LLM down ise?)
```

#### 💾 **brain/memory.py** - HAFIZA
```
memory.py ne yapar?
├─ add(user, reply)           ← Konuşma kaydet
├─ set_pending(action, params) ← Bekleyen işlem kaydet
├─ has_pending()              ← Bekleyen işlem var mı?
├─ fill_pending(input)        ← Eksik parametreyi doldur
└─ get_history()              ← Geçmişi döndür

Ne YAZARSIN burada?
- Yeni state yönetimi (preferences, vb.)
- Kalıcı hafıza (database vb.)
- User profiling
```

#### 🎯 **Skills/skills_manager.py** - AKSIYONLAR
```
skills_manager.py ne yapar?
├─ create_file()        ← Dosya yap
├─ delete_file()        ← Dosya sil
├─ create_folder()      ← Klasör yap
├─ delete_folder()      ← Klasör sil
├─ play_music()         ← Spotify açı
└─ web_search()         ← Google aç

Ne YAZARSIN burada?
- Yeni action (printer, email, vb.)
- Error handling
- Log'lama
```

#### 🛠️ **utils.py** - YARDIMCI ARAÇLAR
```
utils.py ne yapar?
├─ extract_name_from_input()  ← Text'ten isim çıkart
├─ debug_print()              ← Debug mesajı yaz
└─ (Gelecekte daha fazla)

Ne YAZARSIN burada?
- Yeniden kullanılacak fonksiyonlar
- Text işleme helper'ları
- Validation fonksiyonları
```

---

## 5️⃣ Git ve Branch Rehberi

### 🌿 Branch NEDİR?

**Branch = Projenin kopyası** ama paralel çalışan.

Tıpkı ödevde:
- `main` = Final versiyon (öğretmene teslim)
- `develop` = Süründe versiyonu (herkesle çalışıyor)
- `feature/new-feature` = Benim dalım (sadece ben yazıyorum)

```
     main        ← Production (stabil)
      │
      ├─────────────────────────────────
      │
      └─→ develop                      ← Development hub
           │
           ├─→ feature/email (sen çalışıyor)
           ├─→ feature/pdf (başkası çalışıyor)
           └─→ feature/database (başkası çalışıyor)
```

### 📋 BRANCH TABLOSU

| Branch | Amaç | Push Etme Sıklığı | Merge Kime? | Kural |
|--------|------|-------------------|------------|-------|
| **main** | Production, stabil | Nadiren (release) | - | 🔒 PR gerek, test pass |
| **develop** | Development merkez | Her gün | main (release) | 🔒 PR gerek, 1 approval |
| **feature/xxx** | Yeni özellik | Her commit | develop (PR) | ❌ Koruma yok |

### 🎯 Git İŞLEMLERİ - TÜRKÇE AÇIKLAMASI

```bash
# 1. Proje'yi indir (İlk başta 1 kez)
git clone https://github.com/Boranikov/Jarvis_AI.git
cd Jarvis_AI

# 2. Remote'tan güncel bilgi al (her baştan)
git fetch origin

# 3. Develop branch'ine geç (feature başlamadan önce)
git checkout develop
git pull origin develop

# 4. Yeni feature branch oluştur
git checkout -b feature/email-sending
      │
      └─→ "email-sending" = Olay adı
      └─→ "feature/" = Bu bir feature
      └─→ "git checkout -b" = Yeni branch oluştur ve oraya geç

# 5. Kod yaz (Visual Studio Code'da yaz)
# ...dosyaları düzenle...

# 6. Değişiklikleri hazırla (staging)
git add .
     │
     └─→ "." = Tüm dosyaları
     └─→ Değişiklikleri "hazırla" (henüz save etme)

# 7. Hazırlananları kaydet (commit)
git commit -m "feat: Email gönderme özelliği eklendi

- Yeni skill added
- SMTP config
- Attachment support"

# 8. Remote'a gönder (push)
git push -u origin feature/email-sending
         │                    │
         │                    └─→ Remote'a gönder
         └─→ "-u" = Future pushes için remote tracking

# 9. GitHub'da PR açın (Pull Request)
# Browser açıp GitHub'a git
# "Compare & pull request" tıkla
# base: develop, compare: feature/email-sending
# Description yazıp submit et

# 10. Code review tamamlandıktan sonra merge et
# GitHub'da "Merge pull request" tıkla

# 11. Yerel branch'i sil (temizlik)
git branch -d feature/email-sending

# 12. Remote branch'i sil (temizlik)
git push origin --delete feature/email-sending
```

---

## 6️⃣ Başlangıç - Adım Adım

### 🚀 SIFIRDAN BAŞLAMAK

#### **ADIM 1: Kurulum (İlk başta 1 kez)**

```bash
# Terminal/PowerShell aç
# c:\Users\boran\Desktop\Jarvis_Aİ klasörüne git

cd Desktop
cd Jarvis_Aİ

# Python sanal ortam oluştur
python -m venv venv

# Sanal ortamı aç
venv\Scripts\activate
# (Artık "(venv)" göreceksin terminal'de)

# Kütüphaneleri yükle
pip install -r requirements.txt

# Ollama'yı başlat (BAŞKA TERMINAL'DE)
ollama serve
```

#### **ADIM 2: Programı Çalıştır**

```bash
# Sanal ortam aktif değilse aç
venv\Scripts\activate

# Programı çalıştır
python main.py

# Çıkmak için
çık

# veya

exit
```

#### **ADIM 3: Yeni Özellik Eklemek**

**Senaryomu: Email gönderme eklemek istiyorsun**

```bash
# 1. Remote güncellemesini al
git fetch origin

# 2. Develop'e geç
git checkout develop

# 3. Develop'i güncelle
git pull origin develop

# 4. Feature branch oluştur
git checkout -b feature/email-skill

# 5. Kodları yaz
# Dosyaları Visual Studio Code'da düzenle

# === config.py'de ===
ACTION_KEYWORDS = {
    ...
    "send_email": ["gönder", "mail", "email", "e-mail"],
}

REQUIRED_PARAMS = {
    ...
    "send_email": ["to", "subject", "body"],
}

MISSING_QUESTIONS = {
    ...
    "send_email": {
        "to": "Kime göndermek istiyorsun?",
        "subject": "E-mail konusu nedir?",
        "body": "E-mail içeriği nedir?"
    }
}

# === Skills/skills_manager.py'de ===
elif action == "send_email":
    to = params.get("to")
    subject = params.get("subject")
    body = params.get("body")
    
    # Gerçek email gönderme kodu yazıyoruz
    import smtplib
    # ... email kodları ...
    print(f">> [OK] Email gönderildi: {to}")

# === brain/intent_engine.py'de SYSTEM_PROMPT güncelle ===
Allowed actions:
- send_email
# ... ve açıklamasını yaz

# 6. Değişiklikleri hazırla
git add .

# 7. Commit et
git commit -m "feat: Email gönderme özelliği eklendi

- Yeni action: send_email
- Config'e parameterler eklendi
- Skills manager'da email gönderme logic'i
- SMTP konfigürasyonu

Closes #42"
#         ↑
#         GitHub issue numarasını yazarsan otomatik close olur

# 8. Push et
git push -u origin feature/email-skill

# 9. GitHub'da PR aç
# Browser'da git repo
# "Compare & pull request" tıkla
# Açıklama yaz
# Submit et

# 10. Review tamamlanıp approve olunca
# GitHub'da "Merge pull request" tıkla

# 11. Yerel branch'i sil
git branch -d feature/email-skill

# 12. Remote branch'i sil
git push origin --delete feature/email-skill

# 13. Develop'i güncelle (merge'ı almak için)
git checkout develop
git pull origin develop
```

---

## 📊 HIZLI REFERANS

### Git Komutları

| Komut | Ne Yapar? |
|-------|----------|
| `git status` | Şu an durumu göster (değişlikler var mı?) |
| `git log --oneline` | Commit geçmişini göster |
| `git branch` | Şu an hangi branch'deyim? |
| `git branch -a` | Tüm branch'leri göster |
| `git diff` | Neler değişti? |
| `git stash` | Değişiklikleri geçici kaydet |
| `git stash pop` | Geçici kaydı geri al |

### Python Komutları

| Komut | Ne Yapar? |
|-------|----------|
| `python main.py` | Programı çalıştır |
| `pip install package` | Kütüphane yükle |
| `pip freeze` | Kurulu packages göster |
| `python -m venv venv` | Sanal ortam oluştur |

### VSCode Keyboard Shortcuts

| Kısayol | Ne Yapar? |
|---------|----------|
| `Ctrl+S` | Dosyayı kaydet |
| `Ctrl+F` | Arama yap |
| `Ctrl+H` | Find & Replace |
| `Ctrl+/` | Yorum yap (comment) |
| `Alt+Up/Down` | Satırı taşı |
| `Ctrl+Shift+P` | Command palette |

---

## 🎓 ÖRNEK: Email Ekleme

### ADIM ADIM ÖRNEK

#### **1️⃣ config.py'ye Kayıt Et**

```python
# config.py'de ÖNCESİ
ACTION_KEYWORDS = {
    "create_file": [...],
    "play_music": [...]
}

# config.py'de SONRASI
ACTION_KEYWORDS = {
    "create_file": [...],
    "play_music": [...],
    "send_email": ["gönder", "mail", "email"]  # ← YENİ
}
```

#### **2️⃣ Skills/skills_manager.py'ye Ekle**

```python
# ÖNCESİ
elif action == "web_search":
    # ... web search kodu ...

# SONRASI
elif action == "web_search":
    # ... web search kodu ...

elif action == "send_email":  # ← YENİ
    to = params.get("to")
    subject = params.get("subject")
    body = params.get("body")
    
    # Email gönderme mantığı
    try:
        # Gerçek email gönderme kodu
        print(f">> [OK] Email gönderildi: {to}")
    except Exception as e:
        print(f">> [ERROR] Email gönderilemedi: {str(e)}")
```

#### **3️⃣ Intent Engine'e Ekle**

```python
# brain/intent_engine.py'de SYSTEM_PROMPT'da

Allowed actions:
- create_file
- play_music
- web_search
- send_email        ← YENİ

Parameter rules for send_email:
- "to" = email adresi
- "subject" = e-mail konusu
- "body" = e-mail içeriği
```

#### **4️⃣ Git'e Ekle**

```bash
git add config.py Skills/skills_manager.py brain/intent_engine.py
git commit -m "feat: Email gönderme özelliği

- send_email action'ı eklendi
- Email parametreleri tanımlandı
- SMTP entegrasyonu"
git push -u origin feature/email
```

---

## ⚠️ HATA AYIKLAMA

### Sorun: "ModuleNotFoundError: No module named 'ollama'"

**Çözüm:**
```bash
pip install ollama
```

### Sorun: "git: command not found"

**Çözüm:** Git kur: https://git-scm.com/download/win

### Sorun: "Permission denied"

**Çözüm:**
```bash
# PowerShell'de admin olarak aç
# Sonra şu komutu çalıştır:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Sorun: Ollama server down

**Çözüm:**
```bash
# Yeni terminal penceresi açıp
ollama serve
# Bunu çalıştırmaya tut
```

---

## 📚 DÖKÜMANTASYONLAR

| Dosya | İçin? |
|-------|-------|
| [README.md](README.md) | Proje tanıtımı |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Nasıl katkı yaparsın |
| [BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md) | Git Flow detayları |
| [GIT_STRUCTURE_SUMMARY.md](GIT_STRUCTURE_SUMMARY.md) | Git yapısı |

---

## 🎯 CHECKLIST - İlk Katkıdan Sonra

- [ ] Repository fork'ledim
- [ ] Yerel makineme klonladım
- [ ] Sanal ortam oluşturdum
- [ ] Dependencies yükledim
- [ ] Programı çalıştırdım
- [ ] develop branch'e geçtim
- [ ] Feature branch oluşturdum
- [ ] Kod yazdım
- [ ] Test ettim
- [ ] Commit ettim
- [ ] Push ettim
- [ ] PR açtım
- [ ] Code review bekledi
- [ ] Merge oldu
- [ ] Local branch'i sildim

---

**🎉 Tebrikler! Artık tam bir Jarvis contributor'u!**

---

**Son Güncelleme:** 31 Ocak 2026  
**Sorular:** GitHub Issues'den sorabilirsin!

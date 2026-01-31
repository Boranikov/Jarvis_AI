# Contributing to Jarvis AI Assistant

Katkılara açık olduğumuz için teşekkürler! Bu doküman nasıl katkıda bulunabileceğinizi açıklar.

## İçindekiler

- [Başlamadan Önce](#başlamadan-önce)
- [Geliştirme Ortamı Kurulumu](#geliştirme-ortamı-kurulumu)
- [Katkı Türleri](#katkı-türleri)
- [Pull Request Süreci](#pull-request-süreci)
- [Kod Stilleri](#kod-stilleri)
- [Commit Mesajları](#commit-mesajları)

## Başlamadan Önce

1. Repository'yi fork et
2. Yerel makinene clone et
3. Issues'i incele - birisi üzerinde çalışıyor mu kontrol et
4. Yeni bir branch oluştur (bkz. [BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md))

## Geliştirme Ortamı Kurulumu

```bash
# Repository'yi clone et
git clone https://github.com/YOUR_USERNAME/Jarvis_AI.git
cd Jarvis_AI

# Sanal ortam oluştur
python -m venv venv

# Ortamı aktif et
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Kurulum scriptini çalıştır
python setup.py
```

## Katkı Türleri

### 🎯 Yeni Özellik (Feature)

```bash
# develop'den çıkarak yeni branch oluştur
git checkout develop
git checkout -b feature/your-feature-name

# Geliştir ve test et
# ...

# Commit et
git add .
git commit -m "feat: Açıklayıcı başlık

Detaylı açıklama..."

# Remote'a gönder
git push origin feature/your-feature-name

# GitHub'da PR oluştur
```

**Checklist**:
- ✅ Kod test edildi
- ✅ Docstring'ler yazıldı
- ✅ Commit mesajı temiz
- ✅ İlgili Issue referans edildi (Closes #123)

### 🐛 Bug Fix

```bash
# develop'den başla
git checkout develop
git checkout -b fix/bug-name
```

**Checklist**:
- ✅ Bug'un sebebi açıklanıyor
- ✅ Testler pass ediyor
- ✅ Regresyon riskleri kontrol edildi

### 📚 Dokümantasyon

Dokümantasyon hataları doğrudan `main`'e PR gönderilebilir:

```bash
git checkout main
git checkout -b docs/documentation-improvement
```

### 🧪 Test

Test eklemeleri çok değerli:

```bash
git checkout develop
git checkout -b feature/test-suite-improvements
```

**Test Dosyaları Yerleşimi**:
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- Fixtures: `tests/fixtures/`

## Pull Request Süreci

### 1. PR Oluştur

```
Title: [TYPE] Kısa açıklama

Description:
## Açıklama
Ne yaptığını kısaca açıkla.

## Tür
- [ ] 🎯 Yeni özellik
- [ ] 🐛 Bug fix
- [ ] 📚 Dokümantasyon
- [ ] 🧪 Test
- [ ] ♻️ Refactor

## İlgili Issues
Closes #123
Related to #456

## Testing
Nasıl test edileceğini açıkla.

## Checklist
- [ ] Kod test edildi
- [ ] Dokümantasyon güncellendi
- [ ] Yeni bağımlılık eklendi mi? `requirements.txt` güncellendi mi?
- [ ] Commit mesajları temiz
```

### 2. Code Review

- En az 1 approval gereklidir
- CI/CD pipeline'ı pass etmelidir
- Conflicts çözülmelidir

### 3. Merge

- "Squash and merge" tercih edilir
- Branch otomatik silinir

## Kod Stilleri

### Python Stili

PEP 8'i takip et:

```bash
# Code formatting
pip install black
black .

# Linting
pip install flake8
flake8 .

# Type checking
pip install mypy
mypy .
```

### Python Kodlama Kuralları

```python
# ✅ İyi
def extract_name_from_input(user_input: str, action: str) -> str:
    """
    User input'tan keywords kaldırıp ismi çıkar.
    
    Args:
        user_input: Kullanıcı girdisi
        action: Gerçekleştirilecek aksiyon
        
    Returns:
        Çıkarılan isim
    """
    text = user_input.lower().strip()
    return text if text else None

# ❌ Kötü
def extract_name(s, a):
    t = s.lower().strip()
    return t if t else None
```

### Docstring Formatı

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Fonksiyonun kısa açıklaması.
    
    Daha detaylı açıklama paragrafı.
    
    Args:
        param1: Parametrenin açıklaması
        param2: Diğer parametrenin açıklaması
        
    Returns:
        Dönüş değerinin açıklaması
        
    Raises:
        ValueError: Ne zaman raise edilir
    """
    pass
```

## Commit Mesajları

Format: `<type>: <subject>`

```bash
git commit -m "feat: Spotify API entegrasyonu

- Spotify authorized access
- Song search functionality
- Playlist integration

Closes #123"
```

### Types

| Type | Açıklama |
|------|----------|
| `feat` | Yeni özellik |
| `fix` | Bug düzeltme |
| `docs` | Dokümantasyon |
| `style` | Formatting, missing semicolons |
| `refactor` | Kod yapılandırması |
| `perf` | Performans iyileştirmesi |
| `test` | Test ekleme/güncelleme |
| `chore` | Build, dependencies |

## Local Testing Öneri

```bash
# Tüm scriptleri çalıştır
python main.py

# Unit tests (dosya oluştuğü zaman)
python -m pytest tests/

# Linting
flake8 .

# Type checking
mypy .
```

## Sorular?

- 💬 Discussions açabilirsin
- 📧 Issues üzerinden soruları sorun
- 💡 Feature request'ler için yeni Issue oluştur

## Davranış Kuralları

- Saygılı ve yapıcı ol
- Diğer görüşleri dinle
- Spam/NSFW içerik yasak
- Bilimsel tartışmayı tercih et

---

**Teşekkürler! Katkılarınız değerlidir.** 🙏

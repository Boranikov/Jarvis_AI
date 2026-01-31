# Git Branching Strategy

Bu proje **Git Flow** branching stratejisini takip eder.

## Branch Yapısı

### 🎯 Main Branches

#### `main` (Production)
- **Amaç**: Stable, production-ready kodları içerir
- **Kurallar**:
  - Direkt commit yapılmaz
  - Sadece `develop` branch'inden merge alır
  - Her merge'in yanında release tag'i oluşturulur
  - Örnek: `v1.0.0`, `v1.1.0`

#### `develop` (Development)
- **Amaç**: Birleştirilmiş feature'lar ve güncel geliştirme kodu
- **Kurallar**:
  - Feature branch'leri buraya merge edilir
  - PR (Pull Request) ile kontrol edilir
  - CI/CD pipeline'ı çalıştırır

### 🌿 Feature Branches

Feature branch'ler her yeni özellik için oluşturulur.

**Naming Convention**: `feature/<feature-name>`

#### Mevcut Features

1. **`feature/advanced-nlp`**
   - Gelişmiş NLP ve intent recognition
   - Daha iyi language model entegrasyonu
   - Intent engine iyileştirmeleri

2. **`feature/ui-interface`**
   - Kullanıcı arayüzü geliştirmesi
   - Web dashboard (Flask/Django)
   - REST API endpoint'leri

3. **`feature/test-suite`**
   - Unit test'ler
   - Integration test'ler
   - Test coverage raporu

### 🔧 Branch Workflow

#### Yeni Feature Başlatma

```bash
# develop branch'inden başla
git checkout develop
git pull origin develop

# Yeni feature branch oluştur
git checkout -b feature/my-feature-name

# Değişiklikleri yap
git add .
git commit -m "Açıklayıcı commit mesajı"

# Remote'a gönder
git push -u origin feature/my-feature-name
```

#### Pull Request (PR) Oluşturma

1. GitHub'da "New Pull Request" tıkla
2. Base: `develop`, Compare: `feature/my-feature-name`
3. Açıklamasını yazıp submit et
4. Code review'ı bekle
5. Onaylandıktan sonra merge et

#### Feature'ı Tamamladıktan Sonra

```bash
# Yerel branch'i sil
git branch -d feature/my-feature-name

# Remote branch'i sil
git push origin --delete feature/my-feature-name
```

### 🐛 Bug Fix Branches

Acil bug fix'ler için `hotfix/` branch'leri kullanılır.

**Naming Convention**: `hotfix/<bug-name>`

```bash
# main'den çıkar
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug-fix

# Bug'ı düzelt
git add .
git commit -m "Fix: Açıklayıcı mesaj"

# main ve develop'e PR aç
git push -u origin hotfix/critical-bug-fix
```

## Commit Message Konvansiyonu

Temiz commit tarihi için şu format kullanılır:

```
<type>: <subject>

<body>

<footer>
```

### Type

- `feat`: Yeni özellik
- `fix`: Bug düzeltme
- `docs`: Dokümantasyon
- `style`: Kod stili (formatting, missing semicolons, vb.)
- `refactor`: Kodu yeniden yapılandırma
- `perf`: Performans iyileştirmesi
- `test`: Test eklemesi
- `chore`: Build tools, dependencies, vb.

### Örnekler

```
feat: Spotify entegrasyonu eklendi

- Spotify API entegrasyonu
- Müzik arama ve çalma
- Playlist yönetimi

Closes #123
```

```
fix: Intent engine hatasını düzelt

Name parametresi eksik iken system crash oluyordu.
Artık eksik parametreleri kontrol ediyor.

Fixes #456
```

## Tag'ler (Releases)

```bash
# Release tag'i oluştur
git tag -a v1.0.0 -m "Release 1.0.0"

# Remote'a gönder
git push origin v1.0.0
```

## Protected Branches

GitHub'da şu branch'ler korunmalıdır:

- ✅ `main` - Sadece reviewed PR'lar merge edilebilir
- ✅ `develop` - Minimum 1 approval gerekir

## .gitignore Kuralları

Yapılandırıldı - `__pycache__/`, `*.pyc`, `.env`, vb. ignored.

## Useful Commands

```bash
# Tüm branch'leri göster
git branch -a

# Remote'dan fetch et (new branches)
git fetch origin

# Merged branch'leri göster
git branch --merged

# Unmerged branch'leri göster
git branch --no-merged

# Branch'i sil
git branch -d branch-name
git push origin --delete branch-name

# Commit geçmişini görsel olarak göster
git log --oneline --all --graph
```

---

**Son güncelleme**: 31 Ocak 2026

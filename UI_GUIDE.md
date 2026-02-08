# Jarvis AI - Arayüz Geliştirici Rehberi

Bu rehber, Jarvis AI'ın görsel arayüzünü (GUI) anlamak ve özelleştirmek isteyenler içindir.

---

## 📂 Dosya Yapısı ve Görevleri

Arayüz kodu `UI/` klasörü altındadır:

1.  **`UI/main_window.py` (Ana Pencere mantığı)**
    *   Uygulamanın ana çerçevesini çizer.
    *   **Layout (Düzen):** Başlık, sohbet alanı, mesaj kutusu ve butonların yerleşimi buradadır.
    *   **Mantık (Logic):** Mesaj gönderme, AI yanıtını alma, thread yönetimi (`AIWorker`) burada gerçekleşir.

2.  **`UI/styles.qss` (Görsel Tasarım & Renkler)**
    *   CSS benzeri bir stil dosyasıdır.
    *   **Renkler:** Arka plan, yazı rengi, buton renkleri burada tanımlıdır.
    *   **Şekiller:** Köşe yuvarlaklıkları (border-radius), kenarlıklar (border) burada ayarlanır.

3.  **`UI/widgets/chat_bubble.py` (Mesaj Balonları)**
    *   Sohbetteki her bir mesaj kutusunu (balonunu) temsil eden özel bileşendir.
    *   **Boyutlandırma:** Balonun genişliğinin pencereye göre ayarlanması (`resizeEvent`) buradadır.

---

## 🛠️ Nasıl Değiştirilir?

### 1. Renkleri ve Görünümü Değiştirmek
**Dosya:** `UI/styles.qss`

Burada CSS benzeri kodlar göreceksiniz. Değiştirmek istediğiniz bileşeni bulun:

*   **Arka Plan Rengi:** `QMainWindow` veya `QWidget` içindeki `background-color` değerini değiştirin.
    ```css
    QMainWindow {
        background-color: #121212; /* Koyu gri */
    }
    ```
*   **Balon Renkleri:**
    *   Kullanıcı (Sağ): `QLabel#userBubble`
    *   Jarvis (Sol): `QLabel#jarvisBubble`
*   **Yazı Tipi:** `QWidget` altındaki `font-family` değerini değiştirin.

### 2. Pencere Düzenini Değiştirmek
**Dosya:** `UI/main_window.py`

*   **Pencere Boyutu:** `init_ui` metodunda `self.resize(650, 800)` satırını bulun.
*   **Header (Başlık):** `header` değişkeni ile oluşturulan kısım. Logoyu veya başlığı buradan değiştirebilirsiniz.
*   **Input Alanı:** `input_container` kısmını inceleyin.

### 3. Mesaj Balonlarının Şeklini Değiştirmek
**Dosya:** `UI/widgets/chat_bubble.py`

*   **Genişlik Limiti:** Balonların ne kadar uzayacağını `resizeEvent` metodundaki `%85` değerini değiştirerek ayarlayabilirsiniz:
    ```python
    max_width = int(self.parent().width() * 0.85) # %85 genişlik
    ```
*   **Balon Şekli (QSS):** Yuvarlaklıkları veya kenarlıkları `UI/styles.qss` dosyasındaki `border-radius` değerleri ile oynayarak değiştirebilirsiniz.

### 4. Mantık ve İşleyiş (Logic)
**Dosya:** `UI/main_window.py`

*   **AI Yanıtı:** `on_response_received` metodu, AI yanıt verdiğinde ne olacağını belirler.
*   **Mesaj Gönderme:** `send_message` metodu, "Gönder" butonuna basınca çalışır.
*   **Durum Mesajları:** "Düşünüyor...", "Çevrimiçi" yazılarını `send_message` ve `on_response_received` içinde bulabilirsiniz.

---

## 🚀 İpuçları
*   **QSS:** Renkleri değiştirirken Hex kodları kullanın (örn: `#FF0000` kırmızıdır).
*   **Yedekleme:** Büyük değişiklikler yapmadan önce dosyaların yedeğini alın.
*   **Test:** Her değişiklikten sonra uygulamayı yeniden başlatarak sonucu görün. QSS değişiklikleri genellikle yeniden başlatma gerektirir.

"""
Jarvis AI Assistant - Yardımcı Fonksiyonlar
"""

from config import ACTION_KEYWORDS, ATTENTION_WORDS

def remove_ai_name(user_input: str) -> str:
    """Kullanıcı girdisinden AI adını kaldır"""
    ai_names = ["jarvis"]
    text = user_input.lower()
    for name in ai_names:
        text = text.replace(name, " ")
    return " ".join(text.split()).strip()

def extract_name_from_input(user_input: str, action: str) -> str:
    """
    User input'tan keywords ve attention words kaldırıp 
    geriye kalan kısmı name olarak döndür.
    
    Args:
        user_input: Kullanıcı girdisi
        action: Gerçekleştirilecek aksiyon
        
    Returns:
        Çıkarılan isim veya None
    """
    text = user_input.lower().strip()
    
    # Attention words'ünü kaldır
    for word in ATTENTION_WORDS:
        text = text.replace(word, " ")
    
    # Action keywords'ünü kaldır
    keywords = ACTION_KEYWORDS.get(action, [])
    for keyword in keywords:
        text = text.replace(keyword, " ")
    
    # Fazla boşlukları temizle
    name = " ".join(text.split()).strip()
    return name if name else None


def debug_print(message: str, data: dict = None):
    """Debug mesajı yazdır"""
    from config import DEBUG_MODE
    
    if DEBUG_MODE:
        print(f"Debug: {message}")
        if data:
            for key, value in data.items():
                print(f"  - {key}: {value}")

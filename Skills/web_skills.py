"""
Jarvis AI - Web Skills
Web araması işlemleri.
"""

import webbrowser
import urllib.parse


def web_search(params: dict) -> bool:
    """
    Google'da arama yap.
    
    Args:
        params: name içeren dictionary
        
    Returns:
        Başarılı ise True
    """
    query = params.get("name")
    
    if not query:
        print(">> [ERROR] Arama terimi belirtilmedi.")
        return False
    
    try:
        encoded_query = urllib.parse.quote(query)
        webbrowser.open(f"https://www.google.com/search?q={encoded_query}")
        print(f">> [OK] Google'da '{query}' aranıyor...")
        return True
    except Exception as e:
        print(f">> [ERROR] Google açma başarısız: {str(e)}")
        return False

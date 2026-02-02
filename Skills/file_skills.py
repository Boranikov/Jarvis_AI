"""
Jarvis AI - File Skills
Dosya ve klasör işlemleri.
"""

import os
import shutil
from Utils.paths import get_path


def create_file(params: dict) -> bool:
    """
    Dosya oluştur.
    
    Args:
        params: name ve path içeren dictionary
        
    Returns:
        Başarılı ise True
    """
    name = params.get("name")
    location = params.get("path")
    
    if not name:
        print(">> [ERROR] İsim olmadan işlem yapılamaz.")
        return False
    
    target = os.path.join(get_path(location), name)
    
    if "." not in name:
        target += ".txt"
    
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        open(target, "w", encoding="utf-8").close()
        print(f">> [OK] Dosya oluşturuldu: {target}")
        return True
    except Exception as e:
        print(f">> [ERROR] Dosya oluşturma başarısız: {str(e)}")
        return False


def create_folder(params: dict) -> bool:
    """
    Klasör oluştur.
    
    Args:
        params: name ve path içeren dictionary
        
    Returns:
        Başarılı ise True
    """
    name = params.get("name")
    location = params.get("path")
    
    if not name:
        print(">> [ERROR] İsim olmadan işlem yapılamaz.")
        return False
    
    target = os.path.join(get_path(location), name)
    
    try:
        os.makedirs(target, exist_ok=True)
        print(f">> [OK] Klasör oluşturuldu: {target}")
        return True
    except Exception as e:
        print(f">> [ERROR] Klasör oluşturma başarısız: {str(e)}")
        return False


def delete_file(params: dict) -> bool:
    """
    Dosya sil.
    
    Args:
        params: name ve path içeren dictionary
        
    Returns:
        Başarılı ise True
    """
    name = params.get("name")
    location = params.get("path")
    
    if not name:
        print(">> [ERROR] İsim olmadan işlem yapılamaz.")
        return False
    
    target = os.path.join(get_path(location), name)
    
    try:
        if os.path.exists(target):
            os.remove(target)
            print(f">> [OK] Dosya silindi: {target}")
            return True
        else:
            print(f">> [WARNING] Dosya bulunamadı: {target}")
            return False
    except Exception as e:
        print(f">> [ERROR] Dosya silme başarısız: {str(e)}")
        return False


def delete_folder(params: dict) -> bool:
    """
    Klasör sil.
    
    Args:
        params: name ve path içeren dictionary
        
    Returns:
        Başarılı ise True
    """
    name = params.get("name")
    location = params.get("path")
    
    if not name:
        print(">> [ERROR] İsim olmadan işlem yapılamaz.")
        return False
    
    target = os.path.join(get_path(location), name)
    
    try:
        if os.path.exists(target):
            shutil.rmtree(target)
            print(f">> [OK] Klasör silindi: {target}")
            return True
        else:
            print(f">> [WARNING] Klasör bulunamadı: {target}")
            return False
    except Exception as e:
        print(f">> [ERROR] Klasör silme başarısız: {str(e)}")
        return False

#!/usr/bin/env python3
"""
Jarvis AI Assistant - Kurulum Betiği
"""

import os
import subprocess
import sys


def install_dependencies():
    """Bağımlılıkları yükle"""
    print("📦 Bağımlılıklar yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Bağımlılıklar başarıyla yüklendi.")
    except subprocess.CalledProcessError:
        print("✗ Bağımlılık yüklemesi başarısız oldu.")
        return False
    return True


def check_ollama():
    """Ollama kurulu mu kontrol et"""
    print("\n🔍 Ollama kontrolü yapılıyor...")
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Ollama kurulu: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ Ollama kurulu değil.")
    print("  Kurulum: https://ollama.ai/download")
    return False


def pull_model():
    """Modeli indir"""
    print("\n📥 Model indiriliyor: gemma2:2b")
    try:
        subprocess.run(["ollama", "pull", "gemma2:2b"])
        print("✓ Model başarıyla indirildi.")
        return True
    except FileNotFoundError:
        print("✗ Ollama bulunamadı.")
        return False


def main():
    """Kurulum ana fonksiyonu"""
    print("=" * 50)
    print("   Jarvis AI Assistant - Kurulum Betiği")
    print("=" * 50 + "\n")
    
    # Bağımlılıkları yükle
    if not install_dependencies():
        sys.exit(1)
    
    # Ollama kontrolü
    if not check_ollama():
        print("\n⚠️  Ollama kurmanız gerekiyor.")
        print("   https://ollama.ai/download adresinden indirin.")
        sys.exit(1)
    
    # Model kontrolü ve indirme
    print("\nJarvis'i çalıştırmak için gerekli model: gemma2:2b")
    response = input("Modeli indirmek ister misiniz? (e/h): ").lower()
    if response in ["e", "evet", "y", "yes"]:
        if not pull_model():
            print("⚠️  Model indirme başarısız. Elle indirmeyi deneyin:")
            print("   > ollama pull gemma2:2b")
    
    print("\n" + "=" * 50)
    print("✓ Kurulum tamamlandı!")
    print("=" * 50)
    print("\nJarvis'i çalıştırmak için:")
    print("   > python main.py")
    print("\nOllama'yı başlatmak için (ön planda):")
    print("   > ollama serve")


if __name__ == "__main__":
    main()

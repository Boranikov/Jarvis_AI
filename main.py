from brain.intent_engine import process_command
import os

print("Sistem başlatıldı. (Çıkmak için 'çık' yaz)")

while True:
    text = input("\nSen: ")
    if text.lower() in ["çık", "kapat", "exit"]:
        break
    
    # Tek seferde hem aksiyonu hem cevabı alıyoruz (HIZLI)
    result = process_command(text)
    
    action = result.get("action", "unknown")
    reply = result.get("reply", "...")

    # Önce asistanın cevabını yazdıralım
    print(f"Jarvis: {reply}")
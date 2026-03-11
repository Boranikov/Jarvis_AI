import os

def generate_source_txt():
    output_file = "kaynak_kod_dokumu.txt"
    # Dışlanacak klasörler
    ignore_dirs = {
        ".git", "__pycache__", "venv", ".venv", "dist", "build", 
        "assets", "Tests", ".pytest_cache", "Plugins"
    }
    
    # Dışlanacak dosya isimleri
    ignore_files = {"generate_source_txt.py", output_file}

    # Proje kök dizini (script Scripts/ içinde olduğu için bir üst dizin)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, output_file)

    with open(output_path, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk(base_dir):
            # İstenmeyen klasörleri atla
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith((".py", ".md", ".env.example")) and file not in ignore_files:
                    filepath = os.path.join(root, file)
                    # Göreli yol (relative path) hesapla ve formatla
                    rel_path = os.path.relpath(filepath, base_dir).replace("\\", "/")
                    
                    outfile.write("=========================================\n")
                    outfile.write(f"DOSYA: {rel_path}\n")
                    outfile.write("=========================================\n")
                    
                    try:
                        with open(filepath, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"<< DOSYA OKUNAMADI: {e} >>\n")
                    
                    outfile.write("\n\n")
                    
    print(f"Tüm kaynak kodlar başarıyla '{output_path}' dosyasına birleştirildi!")

if __name__ == "__main__":
    generate_source_txt()

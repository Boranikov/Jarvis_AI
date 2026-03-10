import subprocess
from Config.config import get_logger

logger = get_logger("skills.terminal")

def run_terminal_command(command: str) -> str:
    """
    Sistem terminalinde (CMD/Powershell) bir komut çalıştırır ve çıktısını döndürür.
    Bu araç ile sistemde linter çalıştırabilir, kod test edebilir veya dosya dizinlerini listeleyebilirsiniz.
    Windows sisteminde çalışır.
    """
    logger.debug(f"Çalıştırılan komut: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30 # Sonsuz döngüleri önlemek için
        )
        output = result.stdout
        if result.returncode != 0:
            output += f"\nHata Çıktısı:\n{result.stderr}"
            
        return output.strip() if output.strip() else "İşlem başarıyla tamamlandı, çıktı yok."
    except Exception as e:
        logger.error(f"Terminal hatası: {e}")
        return f"Komut çalıştırılırken hata oluştu: {str(e)}"

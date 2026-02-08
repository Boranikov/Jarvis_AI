"""
Jarvis AI - Worker Thread
AI işlemlerini arka planda çalıştırır, UI donmaz.
"""

from PyQt6.QtCore import QThread, pyqtSignal

from Brain.memory import Memory


class AIWorker(QThread):
    """AI işlemlerini arka planda çalıştıran thread"""
    
    # Sinyal: İşlem tamamlandığında yanıtı gönder
    finished = pyqtSignal(str)
    
    def __init__(self, user_text: str, memory: Memory):
        super().__init__()
        self.user_text = user_text
        self.memory = memory
    
    def run(self):
        """Thread çalıştığında bu metot yürütülür"""
        try:
            # Import burada yapılıyor (circular import önlemek için)
            from Core.handler import process_user_input_for_gui
            
            response = process_user_input_for_gui(self.user_text, self.memory)
            self.finished.emit(response)
        except Exception as e:
            self.finished.emit(f"Bir hata oluştu: {str(e)}")

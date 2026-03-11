from typing import Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import os

<<<<<<< HEAD
from Settings.config import DEBUG_MODE
=======
from Config.config import get_logger
>>>>>>> 615e1f8a70867a991aa7761346541130f977e0f8

logger = get_logger("core.display")
console = Console()

if os.name == 'nt':
    os.system('color')

def print_header() -> None:
    console.clear()
    

    ascii_art = r"""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
    """
    console.print(ascii_art, style="bold #2563EB", justify = "center")

    console.print(" Konuşmaya başlamak için mesaj yazın. Çıkmak için 'çık' veya 'exit'.", style="dim white",justify = "center")
    console.print(" /debug on veya /debug off komutları ile log detaylarını değiştirebilirsiniz.\n", style="dim white",justify = "center")

def print_debug(
    action: str,
    path: Optional[str],
    name: Optional[str],
    parameters: Any,
    song_name: Optional[str] = None,
) -> None:
    params_str: str = str(parameters) if isinstance(parameters, dict) and parameters else "{}"
    logger.debug("Action=%s, Path=%s, Name=%s, Params=%s", action, path, name, params_str)

    if action in ["play_music", "play_specific_music", "play_emotion_music"] and song_name:
        logger.debug("Song Name=%s", song_name)

def print_jarvis_response(response: str) -> None:
    console.print(f"\n[bold #3B82F6]Jarvis:[/bold #3B82F6] {response}")
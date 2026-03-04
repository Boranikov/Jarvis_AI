"""
Jarvis AI — MCP Cloud Tools

Nextcloud WebDAV üzerinden bulut dosya okuma/yazma/listeleme araçları.
FastMCP @tool dekoratörü ile tanımlanır.
"""

from typing import Any

from MCP.tool_registry import mcp
from Config.logging_config import get_logger

logger = get_logger("mcp.tools.cloud")

# Nextcloud client referansı — uygulama başlangıcında set edilir
_nextcloud_client = None


def set_cloud_client(client: Any) -> None:
    """NextcloudClient referansını ayarla (lifespan'da çağrılır)."""
    global _nextcloud_client
    _nextcloud_client = client


@mcp.tool()
async def cloud_list(path: str = "/") -> list[dict[str, Any]]:
    """
    Nextcloud'daki klasör içeriğini listele.

    Args:
        path: Klasör yolu (örn: "/Documents", "/Photos")

    Returns:
        Dosya ve klasör bilgileri listesi
    """
    if _nextcloud_client is None:
        return [{"error": "Bulut depolama bağlantısı kurulmamış."}]

    try:
        files = await _nextcloud_client.list_files(path)
        return [
            {
                "name": f.name,
                "path": f.path,
                "is_directory": f.is_directory,
                "size": f.size,
                "content_type": f.content_type,
            }
            for f in files
        ]
    except Exception as exc:
        logger.error("cloud_list_error", path=path, error=str(exc))
        return [{"error": f"Dosya listeleme başarısız: {exc}"}]


@mcp.tool()
async def cloud_read(path: str) -> str:
    """
    Nextcloud'daki bir dosyanın içeriğini oku.

    Args:
        path: Dosya yolu (örn: "/Documents/notes.txt")

    Returns:
        Dosya içeriği (metin olarak)
    """
    if _nextcloud_client is None:
        return "Bulut depolama bağlantısı kurulmamış."

    try:
        content = await _nextcloud_client.read_file(path)
        return content.decode("utf-8", errors="replace")
    except Exception as exc:
        logger.error("cloud_read_error", path=path, error=str(exc))
        return f"Dosya okuma başarısız: {exc}"


@mcp.tool()
async def cloud_write(path: str, content: str) -> str:
    """
    Nextcloud'a dosya yaz veya güncelle.

    Args:
        path: Dosya yolu (örn: "/Documents/notes.txt")
        content: Yazılacak içerik

    Returns:
        Başarı durumu mesajı
    """
    if _nextcloud_client is None:
        return "Bulut depolama bağlantısı kurulmamış."

    try:
        success = await _nextcloud_client.write_file(path, content)
        if success:
            return f"Dosya başarıyla yazıldı: {path}"
        return f"Dosya yazma başarısız: {path}"
    except Exception as exc:
        logger.error("cloud_write_error", path=path, error=str(exc))
        return f"Dosya yazma hatası: {exc}"

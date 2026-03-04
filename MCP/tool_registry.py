"""
Jarvis AI — MCP Tool Registry

FastMCP tabanlı tool kayıt ve yönetim merkezi.
Tüm araçları tek noktada tanımlar ve LLM'in keşfedebileceği formata çevirir.

Kullanım:
    from MCP.tool_registry import mcp, get_all_tool_schemas

    # Tool'ları LLM function calling formatında al
    schemas = get_all_tool_schemas()
"""

from typing import Any

from mcp.server.fastmcp import FastMCP

from logging_config import get_logger

logger = get_logger("mcp.registry")

# ── FastMCP Instance ───────────────────────────────────────

mcp = FastMCP(
    name="Jarvis Tools",
    instructions=(
        "Bu araçlar Jarvis AI asistanının yetenekleridir. "
        "Hafıza yönetimi, bulut dosya erişimi ve bildirim gönderme için kullanılır."
    ),
)


def get_all_tool_schemas() -> list[dict[str, Any]]:
    """
    Tüm kayıtlı MCP tool'ların şemalarını LLM function calling formatında döndür.

    Returns:
        [{"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}, ...]
    """
    tools = mcp.list_tools()
    schemas: list[dict[str, Any]] = []

    for tool in tools:
        schemas.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema or {},
            },
        })

    return schemas


def register_all_tools() -> None:
    """
    Tüm tool modüllerini import ederek tool'ları FastMCP'ye kaydet.
    Bu fonksiyon uygulama başlangıcında (lifespan) çağrılmalıdır.
    """
    # Import side-effect: @mcp.tool() dekoratörleri tool'ları kaydeder
    from MCP.tools import memory_tools  # noqa: F401
    from MCP.tools import cloud_tools  # noqa: F401
    from MCP.tools import notification_tools  # noqa: F401

    logger.info("mcp_tools_registered", count=len(mcp.list_tools()))

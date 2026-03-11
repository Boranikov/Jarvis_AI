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

from Config.logging_config import get_logger

logger = get_logger("mcp.registry")

# ── FastMCP Instance ───────────────────────────────────────

mcp = FastMCP(
    name="Jarvis Tools",
    instructions=(
        "Bu araçlar Jarvis AI asistanının yetenekleridir. "
        "Hafıza yönetimi, bulut dosya erişimi ve bildirim gönderme için kullanılır."
    ),
)


import asyncio

def get_all_tool_schemas() -> list[dict[str, Any]]:
    """
    Tüm kayıtlı MCP tool'ların şemalarını LLM function calling formatında döndür.
    Uyarı: Async loop çakışmalarını önlemek için FastMCP iç verilerini (senkron) kullanır.
    """
    schemas: list[dict[str, Any]] = []

    try:
        tools = mcp._tool_manager.list_tools()
        for tool in tools:
            schemas.append({
                "type": "function",
                "function": {
                    "name": getattr(tool, "name", ""),
                    "description": getattr(tool, "description", ""),
                    "parameters": getattr(tool, "parameters", {}),
                },
            })
    except Exception as exc:
        logger.error(f"MCP Senkron Schema çekme hatası: {exc}")

    return schemas


async def call_mcp_tool_async(name: str, arguments: dict) -> Any:
    """
    Belirli bir MCP aracını asenkron olarak çağırır.

    Args:
        name: Çalıştırılacak aracın adı (örn. 'cloud_list')
        arguments: Aracın parametreleri

    Returns:
        Aracın döndürdüğü sonuç
    """
    try:
        result = await mcp.call_tool(name, arguments)
            
        # FastMCP call_tool returns a tuple, e.g. ([TextContent(...)], {'result': ...})
        if isinstance(result, tuple) and len(result) > 1:
            try:
                # Return the result dict directly for the LLM
                return result[1].get('result', result[1])
            except AttributeError:
                pass
        
        # Fallback to string representation if parsing fails
        return str(result)
        
    except Exception as exc:
        logger.error(f"MCP Tool '{name}' çalıştırılamadı: {exc}")
        return f"MCP Tool Execute Hatası: {exc}"


def register_all_tools() -> None:
    """
    Tüm tool modüllerini import ederek tool'ları FastMCP'ye kaydet.
    Bu fonksiyon uygulama başlangıcında (lifespan) çağrılmalıdır.
    """
    # Import side-effect: @mcp.tool() dekoratörleri tool'ları kaydeder
    from MCP.tools import memory_tools  # noqa: F401
    from MCP.tools import cloud_tools  # noqa: F401
    from MCP.tools import notification_tools  # noqa: F401

    logger.info("mcp_tools_registered")

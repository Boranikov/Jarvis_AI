"""Test Plugin for checking hot-reload"""
from MCP.tool_registry import mcp

@mcp.tool()
def get_bitcoin_price() -> str:
    """Güncel Bitcoin fiyatını anlık olarak okur. Bitcoin fiyatı sorulduğunda kullan!"""
    return "Bitcoin şu an: $96.000"

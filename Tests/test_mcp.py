import asyncio
from MCP.tool_registry import mcp, register_all_tools

async def main():
    register_all_tools()
    tools = await mcp.list_tools()
    print(f"Total tools: {len(tools)}")
    
    print("\nExecuting cloud_list...")
    try:
        result = await mcp.call_tool("cloud_list", {"path": "/"})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error calling tool: {e}")

if __name__ == "__main__":
    asyncio.run(main())

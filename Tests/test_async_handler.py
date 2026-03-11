import asyncio
from Core.async_handler import process_input_async
from Brain.memory import Memory
from Config.settings import get_settings

import asyncio
import httpx
from Skills.skills_manager import get_tool_schemas
from Config.settings import get_settings

async def main():
    s = get_settings()
    from Core.plugin_loader import load_all_plugins
    load_all_plugins()
    from MCP.tool_registry import register_all_tools
    register_all_tools()
    
    tools = get_tool_schemas()
    tools.append({
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "Görevin başarıyla tamamlandığını bildirir.",
            "parameters": {"type": "object", "properties": {"summary": {"type": "string"}}}
        }
    })
    
    # Langchain format to ollama
    ollama_tools = []
    for t in tools:
        ollama_tools.append(t)
        
    payload = {
        "model": s.fast_model,
        "messages": [
            {"role": "system", "content": "Sen Jarvis'sin, yapay zeka asistanı. Sana verilen araçları kullanarak kullanıcının isteklerini yerine getirmelisin."},
            {"role": "user", "content": "Güncel bitcoin fiyatı nedir?"}
        ],
        "tools": ollama_tools,
        "stream": False,
        "options": {"temperature": 0.0}
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{s.ollama_base_url}/api/chat", json=payload, timeout=30)
        print(resp.json())

if __name__ == "__main__":
    asyncio.run(main())

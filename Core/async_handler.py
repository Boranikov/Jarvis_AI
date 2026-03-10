"""
Jarvis AI — Async Input Handler

Faz 5: LangGraph Entegrasyonu (FastAPI Uyumlu)
Mevcut async_handler.py tamamen yenilenerek Brain/graph_router üzerinden
çalışacak şekilde güncellenmiştir.
"""

from typing import Any

from langchain_core.messages import HumanMessage

from Brain.memory import Memory
from Config.logging_config import get_logger
from Config.settings import JarvisSettings
from Brain.graph_router import app

logger = get_logger("core.async_handler")

async def process_input_async(
    user_input: str,
    memory: Memory,
    user_id: str,
    settings: JarvisSettings,
) -> dict[str, Any]:
    """
    Ana async orkestratör — FastAPI endpoint'i tarafından çağrılır.
    
    Tüm karmaşık mantık (eski nesil intent_engine vs.) LangGraph
    (app) içerisine devredilmiştir.
    """
    # Ana LangGraph Çağrısı
    logger.debug("Tüm komutlar (Async) LangGraph'a (Orchestrator) gönderiliyor.")
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "error": None
    }
    
    try:
        # LangGraph ainvoke ile çalıştırıyoruz
        final_state = await app.ainvoke(initial_state)
    except Exception as exc:
        logger.error("langgraph_ainvoke_error", error=str(exc))
        return {
            "response": "Sistemsel bir hata oluştu Efendim.",
            "action_taken": "error"
        }
    
    messages = final_state.get("messages", [])
    action_taken = "unknown"
    reply = "Üzgünüm, bir hata oluştu ve yanıt üretemedim Efendim."
    
    if messages:
        last_message = messages[-1]
        
        # Eğer bir ToolMessage ya da tool_calls içeren bir mesaj ise
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tc in last_message.tool_calls:
                 if tc["name"] == "finish_task":
                     reply = tc["args"].get("summary", "İşlemleriniz tamamlandı Efendim.")
                     action_taken = "finish_task"
                     break
            else:
                 reply = last_message.content if last_message.content else "İşlem yapıldı Efendim."
                 action_taken = last_message.tool_calls[-1]["name"]
                 
        elif hasattr(last_message, "content") and last_message.content:
            # Sadece metin geldiyse
            reply = last_message.content
            action_taken = "chat"
            
    # Hafızaya ekle
    memory.add(user_input, reply)

    return {
        "response": reply,
        "action_taken": action_taken
    }

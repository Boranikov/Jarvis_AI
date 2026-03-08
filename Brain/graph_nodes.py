from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, ToolMessage

from Config.config import FAST_MODEL
from Skills.skills_manager import get_tool_schemas, perform_skill
from Brain.graph_state import JarvisState

# Performans için LLM'in global olarak tanımlanması (Döngüde sürekli yaratılmasını önler)
_llm = ChatOllama(
    model=FAST_MODEL,
    temperature=0.0
)
_tools = get_tool_schemas()
_llm_with_tools = _llm.bind_tools(_tools)


def agent_node(state: JarvisState) -> JarvisState:
    """Mesaj geçmişini alır, karar verir ve LLM'i tetikler."""
    messages = state["messages"]
    
    response = _llm_with_tools.invoke(messages)

    return {"messages": [response], "error": None}


def tool_node(state: JarvisState) -> JarvisState:
    """Agent'ın bağladığı araçları (skills) çalıştırır ve sonucunu döner."""
    messages = state["messages"]
    last_message = messages[-1]

    # Mesaj türü AIMessage değilse veya içinde tool çağırma yoksa geç
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return {"messages": [], "error": "Tool call bulunmadı"}
    
    tool_messages = []
    
    for tool_call in last_message.tool_calls:
        action_name = tool_call["name"]
        args = tool_call["args"]
        
        try:
            result = perform_skill(action_name, args)
            tool_res_str = f"Başarılı. Sonuç: {result}"
        except Exception as e:
            tool_res_str = f"Hata: {str(e)}"
            
        tool_messages.append(
            ToolMessage(
                content=str(tool_res_str),
                name=action_name,
                tool_call_id=tool_call["id"]
            )
        )
        
    return {"messages": tool_messages, "error": None}
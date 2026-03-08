import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import AIMessage, ToolMessage
from Config.config import FAST_MODEL
from Skills.skills_manager import get_tool_schemas, perform_skill
from Brain.graph_state import JarvisState

# Node 1: LLM
def agent_node(state: JarvisState) -> JarvisState:
    """Mesaj geçmişini alıp Ollama'ya gönderen ve Tool çağrısını tetikleyen düğüm."""
    messages = state["messages"]
    #LangChain ChatOllama nesnesini oluştur
    # Localhost varsayılan olarak tanımlıdır

    llm = ChatOllama(
        model = FAST_MODEL,
        temperature = 0.0
    )

    # Native Tool şemaları yükle
    tools= get_tool_schemas()
    llm_with_tools = llm.bind_tools(tools)

    #LLM çağır
    response = llm_with_tools.invoke(messages)

    # Yeni cevabı listeye ekle
    return {"messages": [response],"error": None}

# Node: Tools

def tool_node(state: JarvisState) -> JarvisState:
    """Agent'ın çağırdığı araçları gerçekten çalıştıran düğüm."""

    messages = state["messages"]

    # Son mesajı al
    last_message = messages[-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        # Araç çağıracak bir şey yoksa geç
        return {"messages": [], "error": "Tool call bulunmadı"}
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        action_name = tool_call["name"]
        args = tool_call["args"]
        try:
            result = perform_skill(action_name, args)
            tool_res_str = f"Success. Result: {result}"
        except Exception as e:
            tool_res_str = f"Error: {str(e)}"
            tool_messages.append(
            ToolMessage(
                content=str(tool_res_str),
                name=action_name,
                tool_call_id=tool_call["id"]
            )
        )
        
    return {"messages": tool_messages, "error": None}
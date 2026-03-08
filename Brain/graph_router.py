from langgraph.graph import StateGraph, END
from Brain.graph_state import JarvisState
from Brain.graph_nodes import agent_node, tool_node

def should_continue(state: JarvisState) -> str:
    """Agent düğümünden sonra akışın nereye gideceğine karar verir."""
    last_message = state["messages"][-1]
    
    # Model araç çağırdıysa -> Tools düğümüne git
    if last_message.tool_calls:
        return "tools"
    
    # Araç çağrısı yoksa, model doğrudan metin yanıtı üretmiştir -> Bitir
    return "end"

# 1. Grafiği başlat
workflow = StateGraph(JarvisState)

# 2. Düğümleri grafiğe ekle
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# 3. Giriş noktası her zaman Agent'tır
workflow.set_entry_point("agent")

# 4. Agent'tan çıkarken nereye gidileceğini Router'a (should_continue) bırak
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END
    }
)

# 5. Tools düğümü işini bitirdiğinde her zaman tekrar Agent'a döner (sonucu iletmek için)
workflow.add_edge("tools", "agent")

# Dışarıdan import edilecek ana uygulama (Graph)
app = workflow.compile()

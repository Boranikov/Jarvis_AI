from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, ToolMessage

from Config.config import FAST_MODEL
from Skills.skills_manager import get_tool_schemas, perform_skill
from Brain.graph_state import JarvisState

# Agent'ın süreci sonlandırmak için kullanacağı dummy (sahte) yetenek
def finish_task(summary: str) -> str:
    """Görevin başarıyla tamamlandığını bildirir ve bir özet sunar."""
    return summary

# Performans İyileştirmesi: LLM ve Tool Şemalarını Düğüm (Node) Dışında Sadece Bir Kere Yükle
_llm = ChatOllama(
    model=FAST_MODEL,
    base_url="http://127.0.0.1:11434",
    temperature=0.0
)
_tools = get_tool_schemas()

# finish_task aracını schema listesine manuel ekliyoruz
_tools.append({
    "type": "function",
    "function": {
        "name": "finish_task",
        "description": "Görevin başarıyla tamamlandığını bildirir ve bir özet sunar. Kullanıcının istekleri karşılandığında döngüyü bitirmek için ÇAĞRILMAK ZORUNDADIR.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Kullanıcıya sunulacak final özet mesajı."
                }
            },
            "required": ["summary"]
        }
    }
})

_llm_with_tools = _llm.bind_tools(_tools)


from langchain_core.messages import SystemMessage

async def agent_node(state: JarvisState) -> JarvisState:
    """Mesaj geçmişini alır, karar verir ve LLM'i tetikler."""
    messages = state["messages"]
    
    # RAG ve sistem özel talimatları
    sys_prompt = SystemMessage(content=(
        "Sen Jarvis'sin, yapay zeka asistanı. Sana verilen araçları (tools) "
        "kullanarak kullanıcının isteklerini yerine getirmelisin.\n"
        "- Cevapların KUSURSUZ, DOĞAL ve DİLBİLGİSİ KURALLARINA UYGUN TÜRKÇE olmalıdır. İngilizce kelimeleri veya bozuk çeviri kokan cümleleri ASLA kullanma.\n"
        "- Kısa, net ve direkt çözüme odaklı cevaplar ver.\n"
        "- Kullanıcı belli bir şarkıyı çalmanı istediğinde 'play_specific_music' aracını kullan. Şarkı adını ve sanatçıyı ayırarak gönder.\n"
        "- Araçlardan (tools) gelen sonuçları KULLANICIYA DOĞAL BİR ŞEKİLDE AKTAR. Örneğin müzik başarıyla çalınırsa, araçtan gelen gerçek sanatçı ve şarkı ismini kullanarak nazikçe bilgi ver.\n"
        "- İSİM, MESLEK, TERCİH, YAŞ gibi kullanıcıyla ilgili ÖNEMLİ KİŞİSEL BİLGİLER verildiğinde anında 'store_long_term_memory' aracını çağırıp hafızana kaydet.\n"
        "- Kullanıcı 'benim adım ne' veya geçmişle alakalı bir şey sorarsa KESİNLİKLE 'search_long_term_memory' aracını kullanarak cevabı veri tabanında ara ve bulduğunu kullanıcıyla paylaş.\n"
        "- Yanıtlarını mutlaka 'Efendim' hitabıyla bitir."
    ))
    
    # Sistem mesajını en başa ekleyip LLM'e yolluyoruz
    response = await _llm_with_tools.ainvoke([sys_prompt] + messages)

    return {"messages": [response], "error": None}


async def tool_node(state: JarvisState) -> JarvisState:
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
        
        if action_name == "finish_task":
            # Özel dummy aracımız, sadece argümanlardan summary bilgisini alıp dönecek
            result = finish_task(args.get("summary", "Görev tamamlandı."))
            tool_res_str = f"Başarılı. Sonuç: {result}"
        else:
            try:
                result = await perform_skill(action_name, args)
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
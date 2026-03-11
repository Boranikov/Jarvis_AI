"""
Jarvis AI - Coding Engine

qwen2.5-coder:14b modeli ile kodlama, hata ayıklama ve proje yönetimi.
Otonom LangGraph Node ve Edges implementasyonu ile State Machine tabanlı çalışır.
"""

import json
from typing import Any, Optional, Annotated, TypedDict
import operator

import ollama
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver

from Config.config import CODING_MODEL, get_logger, MAX_TOOL_ITERATIONS, SAFETY_MODE
from Config.settings import get_settings
from Skills.skills_manager import perform_skill

logger = get_logger("brain.coding")

_DESTRUCTIVE_TOOLS: frozenset[str] = frozenset({"write_to_file", "delete_file"})
_DEFAULT_PROJECT_PATH: str = "Desktop"

SYSTEM_PROMPT: str = """
SEN: Jarvis'in Kıdemli Baş Yazılım Mühendisisin (Lead Software Engineer).
GÖREVİN: Kullanıcının kodlama isteklerini çözmek, proje oluşturmak, hataları ayıklamak ve tam çalışan kod yazmak.
MODELİN: Qwen 2.5 Coder.
VARSAYILAN PROJE YOLU: {default_path}
Kullanıcı başka bir yol belirtmezse projeleri bu yolda oluştur.

--- MUTLAK YASAK LİSTESİ (BUNLARI YAPARSAN BAŞARISIZ OLURSUN) ---
- ASLA `pass` yazma.
- ASLA `# buraya yazın`, `# TODO`, `# ...`, `# burayı doldurun` gibi placeholder yorum yazma.
- ASLA iskelet/stub/boş fonksiyon yazma. Her fonksiyon ÇALIŞIR kod içermeli.
- ASLA "geri kalanı aynı" veya "..." ile kod kısaltma.
- Her dosya, python3 ile çalıştırıldığında HATASIZ çalışmalıdır.

--- BÜYÜK PROJE TALİMATI ---
Birden fazla dosya yazman gerekiyorsa:
- Her `write_to_file` çağrısında tek bir dosyanın TAM ve ÇALIŞIR kodunu yaz.
- Sonraki adımda bir sonraki dosyayı yaz.
- Tüm dosyalar bitene kadar final_answer verme.
- Dosyalar arası import'ları doğru yaz.

--- MEVCUT ARAÇLARIN (TOOLS) ---
Kritik Not: Araçları çağırırken GEREKLİ TÜM parametreleri (name, path, content vb.) eksiksiz gönder.

1. `list_dir_recursive`
   - Amaç: Klasördeki dosya ağacını görmek.
   - Parametre: {{"path": "klasör_yolu"}}

2. `read_file`
   - Amaç: Dosya içeriğini okumak.
   - Parametre: {{"path": "klasör_yolu", "name": "dosya_adi"}}

3. `write_to_file`
   - Amaç: Dosya oluşturmak veya içeriğini güncellemek (üzerine yazar).
   - KURAL: Dosyanın ÇALIŞIR HALDEKİ TAMAMINI yaz. İçi boş fonksiyon veya pass YASAK.
   - Parametre: {{"path": "klasör_yolu", "name": "dosya_adi", "content": "tam_çalışan_kod"}}

4. `delete_file`
   - Amaç: Dosya silmek.
   - Parametre: {{"path": "klasör_yolu", "name": "dosya_adi"}}

--- ÇALIŞMA PROTOKOLÜ ---
1. ANALİZ ET: İsteği anla.
2. KEŞFET (`list_dir_recursive`): Gerekiyorsa dosya yapısını kontrol et.
3. OKU (`read_file`): Değiştireceğin dosyayı oku.
4. PLANLA: Neyi neden değiştireceğini düşün.
5. UYGULA (`write_to_file`): Kodu tam, eksiksiz ve ÇALIŞIR şekilde yaz.
6. BİTİR (`final_answer`): TÜM dosyalar yazıldıktan sonra sonucu bildir.

--- KRİTİK KURAL ---
Cevabın HER ZAMAN ve SADECE geçerli bir JSON objesi olmalıdır.
Markdown kullanma. Açıklama ekleme. Sadece JSON.

--- ÇIKTI FORMATI (SADECE JSON) ---
{{
  "thought": "...",
  "tool": "write_to_file",
  "args": {{...}},
  "response": "Sadece final_answer için"
}}
""".format(default_path=_DEFAULT_PROJECT_PATH)

class CodingState(TypedDict):
    """Coding Graph State"""
    messages: Annotated[list[dict], operator.add]
    actions_taken: Annotated[list[dict], operator.add]
    iterations: int
    final_response: str


def _execute_tool(tool_name: str, args: dict[str, Any]) -> str:
    """Araç çağrısını çalıştır ve sonucu string olarak döndür."""
    # Handle unexpected exception internally inside execute_tool
    try:
        result = perform_skill(tool_name, args)
        if result is False:
             return f"HATA: '{tool_name}' işlemi başarısız oldu. Gerekli parametrelerin (name, path, content vb.) tam ve doğru olduğundan emin ol."
        if isinstance(result, bool):
            return "İşlem başarılı."
        if isinstance(result, str):
            return result
        return str(result)
    except Exception as exc:
        return f"Aracı çalıştırırken hata oluştu: {str(exc)}"


def agent_node(state: CodingState) -> dict:
    messages = state.get("messages", [])
    try:
        response = ollama.chat(
            model=CODING_MODEL,
            messages=messages,
            format="json",
            options={"temperature": 0.2},
        )
        result = json.loads(response.message.content)
        return {"messages": [{"role": "assistant", "content": json.dumps(result, ensure_ascii=False)}]}
    except Exception as exc:
        logger.error("Coding Engine hatası: %s", exc, exc_info=True)
        err_payload = {"tool": "final_answer", "response": f"Dahili Hata: {exc}", "args": {}}
        return {"messages": [{"role": "assistant", "content": json.dumps(err_payload, ensure_ascii=False)}]}


def tool_node(state: CodingState) -> Command[str]:
    messages = state["messages"]
    last_message = messages[-1]
    
    try:
        result = json.loads(last_message["content"])
    except:
        return Command(goto="agent")
         
    tool = result.get("tool", "final_answer")
    args = result.get("args", {})
    thought = result.get("thought", "")
    
    if thought:
        logger.debug("Düşünce: %s", thought[:150])
    
    if tool == "final_answer":
        return Command(update={"final_response": result.get("response", "İşlem tamamlandı.")}, goto=END)

    settings = get_settings()
    
    # Check Destructive Tools
    if SAFETY_MODE and tool in _DESTRUCTIVE_TOOLS:
        file_name = args.get("name", "bilinmeyen")
        content_preview = args.get("content", "")[:300]
        
        # Human in the loop interaction using LangGraph interrupt
        prompt_msg = f"Onay Bekleniyor: {tool} işlemi ({file_name}). Önizleme: {content_preview}"
        logger.info(prompt_msg)
        
        # We interrupt execution and wait for outside code to resume us
        user_response = interrupt({
            "type": "authorization_required",
            "action": tool,
            "args": args,
            "message": prompt_msg
        })
        
        approved = False
        if isinstance(user_response, bool):
            approved = user_response
        elif isinstance(user_response, str) and user_response.lower() in ("e", "evet", "y", "yes"):
            approved = True
            
        if not approved:
            return Command(
                update={
                    "actions_taken": [{"tool": tool, "args": args, "status": "rejected"}],
                    "messages": [{"role": "user", "content": "KULLANICI BU İŞLEMİ REDDETTİ. Başka bir yol dene veya final_answer ile bitir."}],
                    "iterations": state["iterations"] + 1
                },
                goto="agent"
            )

    # Execute tool
    logger.debug("Araç çalıştırılıyor: %s", tool)
    tool_output = _execute_tool(tool, args)
    logger.debug("Araç sonucu [%s]: %.200s", tool, tool_output)
    
    update_dict = {
        "actions_taken": [{"tool": tool, "args": args, "status": "executed", "output_preview": tool_output[:300]}],
        "messages": [{"role": "user", "content": f"ARAÇ SONUCU ({tool}):\n{tool_output}\n\nBir sonraki adımına geç. Cevabın SADECE JSON olsun."}],
        "iterations": state["iterations"] + 1
    }
    
    return Command(
        update=update_dict,
        goto="agent"
    )

def should_continue(state: CodingState) -> str:
    if state["iterations"] >= MAX_TOOL_ITERATIONS:
        return "error_handler"
    return "tools"

def error_handler(state: CodingState) -> dict:
    logger.warning("Coding döngüsü maksimum iterasyona ulaştı (%d)", MAX_TOOL_ITERATIONS)
    return {"final_response": "Maksimum adım sayısına ulaşıldı Efendim. Yapılan işlemler kaydedildi."}

coding_graph = StateGraph(CodingState)
coding_graph.add_node("agent", agent_node)
coding_graph.add_node("tools", tool_node)
coding_graph.add_node("error_handler", error_handler)

coding_graph.set_entry_point("agent")
coding_graph.add_conditional_edges("agent", should_continue, ["tools", "error_handler"])
coding_graph.add_edge("error_handler", END)

# Persistent checkpointer ekleyebiliriz (SqliteSaver vb.), şimdilik memory'de kalsın.
memory_saver = MemorySaver()
coding_app = coding_graph.compile(checkpointer=memory_saver)

def process_coding_task(user_input: str, file_context: str = "") -> dict[str, Any]:
    """
    Kodlama isteğini asenkron yetenekli LangGraph state machine ile işler.
    
    Args:
        user_input: Kullanıcı girdisi
        file_context: Ek bağlam bilgisi (opsiyonel)

    Returns:
        {"success": bool, "response": str, "actions_taken": list}
    """
    prompt: str = f"KULLANICI İSTEĞİ: {user_input}\n"
    if file_context:
        prompt += f"\nGENEL BAĞLAM:\n{file_context}\n"
        
    initial_state = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "actions_taken": [],
        "iterations": 0,
        "final_response": ""
    }
    
    config = {
        "configurable": {"thread_id": "coding_task_1"},
        "recursion_limit": MAX_TOOL_ITERATIONS * 3
    }
    
    try:
        final_state = coding_app.invoke(initial_state, config=config)
        return {
            "success": True,
            "response": final_state.get("final_response", ""),
            "actions_taken": final_state.get("actions_taken", [])
        }
    except Exception as exc:
        logger.error("Coding task sırasında grafikte kesilme/hata: %s", exc)
        return {
            "success": False,
            "response": f"İşlem sırasında beklenmedik bir hata oluştu: {exc}",
            "actions_taken": []
        }
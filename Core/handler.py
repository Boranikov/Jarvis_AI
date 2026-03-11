"""
Jarvis AI - Input Handler

Kullanıcı girdisi işleme ve engine routing.
"""

from enum import Enum
from typing import Optional

from Brain.memory import Memory
<<<<<<< HEAD
from Skills.skills_manager import perform_skill
from Core.display import print_debug    
from Settings.config import PRESENCE_TRIGGERS
=======
from Core.display import print_debug
from Config.config import get_logger

from langchain_core.messages import HumanMessage
from Brain.router import classify_intent, detect_emotion
from Brain.coding_engine import process_coding_task
from Brain.reasoning_engine import process_reasoning, format_reasoning_response
from Brain.graph_router import app

logger = get_logger("core.handler")

class OutputMode(Enum):
    """Çıktı modu: CLI print tabanlı, GUI return tabanlı."""
    CLI = "cli"
    GUI = "gui"

async def process_input(
    user_input: str,
    memory: Memory,
    mode: OutputMode = OutputMode.CLI,
) -> Optional[str]:
    """Birleşik kullanıcı girdi işleyici."""
    
    # Presence shortcut (Eğer sadece orda mısın diye soruyorsa hızlı cevap)
    normalized = user_input.lower().strip()
    presence_triggers = (
        "jarvis orda mısın", "jarvis orada mısın", 
        "hey jarvis orda mısın", "hey jarvis orada mısın", "orda mısın", "orada mısın"
    )
    if any(trigger in normalized for trigger in presence_triggers):
        reply = "Sizin için her zaman buradayım efendim."
        if mode == OutputMode.CLI:
            from Core.display import print_jarvis_response
            print_jarvis_response(reply)
        return reply if mode == OutputMode.GUI else None
    
    # 1. Niyet Analizi (Semantic Routing)
    intent = classify_intent(user_input)
    logger.debug(f"Tespit edilen niyet: {intent}")

    # 2. Rotalama
    if intent == "coding":
        return await _handle_coding_task(user_input, memory, mode)
    elif intent == "reasoning":
        return await _handle_reasoning_task(user_input, memory, mode)
    
    # Varsayılan: Hızlı Model / LangGraph
    logger.debug("Komut LangGraph'a (Fast Model) gönderiliyor.")
    return await _handle_fast_model(user_input, memory, mode)
>>>>>>> 615e1f8a70867a991aa7761346541130f977e0f8


async def _handle_coding_task(user_input: str, memory: Memory, mode: OutputMode) -> Optional[str]:
    """Kodlama isteklerini uzman CodingEngine'e gönderir."""
    logger.debug("Kodlama isteği uzman Coding Engine'e yönlendiriliyor...")
    
    # Coding Engine senkron çalışıyor (kendi içinde loop barındırdığı için), thread'de çalıştır
    import asyncio
    result = await asyncio.to_thread(process_coding_task, user_input)
    
    reply = result.get("response", "Kodlama işlemi tamamlanamadı Efendim.")
    
    if mode == OutputMode.CLI:
        from Core.display import print_jarvis_response
        print_jarvis_response(reply)
    
    memory.add(user_input, reply)
    return reply if mode == OutputMode.GUI else None


async def _handle_reasoning_task(user_input: str, memory: Memory, mode: OutputMode) -> Optional[str]:
    """Mantıksal/Düşünsel istekleri ReasoningEngine'e gönderir."""
    logger.debug("Muhakeme isteği uzman Reasoning Engine'e yönlendiriliyor...")
    
    emotion_ctx = detect_emotion(user_input)
    
    import asyncio
    result = await asyncio.to_thread(process_reasoning, user_input, emotion_ctx)
    
    reply = format_reasoning_response(result)
    
    if mode == OutputMode.CLI:
        from Core.display import print_jarvis_response
        print_jarvis_response(reply)
        
    # Eğer çalıştırılabilir adımlar varsa, onları da uygula (Basit implementasyon)
    if result.get("executable_steps"):
        from Skills.skills_manager import perform_skill
        for step in result["executable_steps"]:
            action = step.get("action")
            params = step.get("params", {})
            if action:
                await perform_skill(action, params)

    memory.add(user_input, reply)
    return reply if mode == OutputMode.GUI else None


async def _handle_fast_model(
    user_input: str,
    memory: Memory,
    mode: OutputMode,
    emotion_context: Optional[dict] = None,
) -> Optional[str]:
    """
    LangGraph tabanlı yeni merkezi orkestratör.
    Eski intent engine ve spagetti if-else bloklarının yerini alır.
    Tüm süreçleri (akıl yürütme, kodlama, tool çağırma) LangGraph State Machine yönetir.
    """
    logger.debug("LangGraph Orkestratörü başlatılıyor...")
    
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "error": None
    }
    
    # Grafiği çalıştır
    final_state = await app.ainvoke(initial_state)
    
    # Final dönen cevapları al
    messages = final_state.get("messages", [])
    if not messages:
        reply = "Üzgünüm, bir hata oluştu ve yanıt üretemedim Efendim."
    else:
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tc in last_message.tool_calls:
                 if tc["name"] == "finish_task":
                     reply = tc["args"].get("summary", "İşlemleriniz tamamlandı Efendim.")
                     break
            else:
                 reply = last_message.content if last_message.content else "İşlem yapıldı Efendim."
        else:
            reply = last_message.content if hasattr(last_message, "content") else str(last_message)
            
    if mode == OutputMode.CLI:
        from Core.display import print_jarvis_response
        print_jarvis_response(reply)
        
    memory.add(user_input, reply)

    return reply if mode == OutputMode.GUI else None

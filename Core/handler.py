"""
Jarvis AI - Input Handler
Kullanıcı girdisi işleme ve model routing.
"""

from Brain.router import classify_intent, detect_emotion
from Brain.intent_engine import process_command
from Brain.reasoning_engine import process_reasoning, format_reasoning_response
from Brain.plan_executor import execute_plan, format_execution_result
from Brain.memory import Memory
from Skills.skills_manager import perform_skill
from Core.display import print_debug
from Utils.math_validator import (
    validate_math_response, format_validation_result,
    llm_failed_to_solve, solve_directly
)
from config import PRESENCE_TRIGGERS, DEBUG_MODE


def handle_presence_check(user_input: str) -> bool:
    """Sistem kontrolü yapılıyor mu kontrol et"""
    normalized = user_input.lower()
    if any(t in normalized for t in PRESENCE_TRIGGERS):
        print("Jarvis: Sizin için her zaman buradayım efendim.")
        return True
    return False


def process_user_input(user_input: str, memory: Memory):
    """
    Kullanıcı girdisini işle.
    Router ile hangi modelin kullanılacağına karar verilir.
    """
    
    # === ROUTING ===
    route = classify_intent(user_input)
    emotion_context = detect_emotion(user_input)
    
    if DEBUG_MODE:
        print(f">> [ROUTER] Model: {'qwen2.5:7b (reasoning)' if route == 'reasoning' else 'qwen2.5:3b (fast)'}")
        if emotion_context.get("detected"):
            print(f">> [ROUTER] Duygu: {emotion_context.get('category')} - {emotion_context.get('keywords')}")
    
    # === REASONING MODEL ===
    if route == "reasoning":
        result = process_reasoning(user_input, emotion_context)
        
        if result.get("success"):
            response = format_reasoning_response(result)
            
            # === LLM BAŞARISIZSA SYMPY/NUMPY DEVREYE GİRSİN ===
            if llm_failed_to_solve(response):
                if DEBUG_MODE:
                    print(">> [MATH] LLM çözemedi, sympy/numpy devreye giriyor...")
                
                direct_result = solve_directly(user_input)
                if direct_result["success"]:
                    response = f"{direct_result['explanation']} Efendim."
                    print(f"Jarvis: {response}")
                    print(f">> [MATH] ✓ {direct_result['method']} ile hesaplandı: {direct_result['result']}")
                else:
                    print(f"Jarvis: {response}")
                    if direct_result["explanation"]:
                        print(f">> [MATH] {direct_result['explanation']}")
            else:
                print(f"Jarvis: {response}")
                
                # === MATEMATİK DOĞRULAMA (Hibrit) ===
                validation = validate_math_response(user_input, response)
                if validation["validated"]:
                    validation_msg = format_validation_result(validation)
                    if validation_msg:
                        print(f">> [MATH] {validation_msg}")
            
            # Çalıştırılabilir adımlar varsa yürüt
            executable_steps = result.get("executable_steps")
            if executable_steps:
                if DEBUG_MODE:
                    print(f">> [PLAN] {len(executable_steps)} adım yürütülecek...")
                
                execution_result = execute_plan(executable_steps)
                execution_message = format_execution_result(execution_result)
                
                if execution_message:
                    print(f"Jarvis: {execution_message}")
                    response += execution_message
            
            # Hafızaya ekle
            memory.add(user_input, response)
        else:
            print(f"Jarvis: {result.get('response', 'Bir sorun oluştu Efendim.')}")
        
        return
    
    # === FAST MODEL (Intent Engine) ===
    result = process_command(user_input, memory.get_history())
    
    action = result.get("action", "unknown")
    reply = result.get("reply", "Efendim?")
    path = result.get("path")
    name = result.get("name")
    song_name = result.get("song_name")
    original_action = result.get("original_action")
    parameters = result.get("parameters", {})
    
    # Parameters'ın dict olmasını garantile
    if not isinstance(parameters, dict):
        parameters = {}
    
    # Yanıtı göster
    print(f"Jarvis: {reply}")
    print_debug(action, path, name, parameters, song_name)
    
    # === EKSİK PARAMETRE YÖNETİMİ ===
    if action == "missing_parameters":
        if original_action and parameters.get("missing"):
            # Orijinal parametreleri (path gibi) sakla
            original_params = {}
            if path:
                original_params["path"] = path
            if name:
                original_params["name"] = name
            if song_name:
                original_params["song_name"] = song_name
            memory.set_pending(original_action, parameters.get("missing", []), original_params)
        return
    
    # === PARAMETRELERI DOLDUR ===
    if path:
        parameters["path"] = path
    if name:
        parameters["name"] = name
    if song_name:
        parameters["song_name"] = song_name
    
    # Path varsayılanını belirle (dosya/klasör işlemleri için)
    if action in ["create_file", "create_folder", "delete_file", "delete_folder"]:
        if not parameters.get("path"):
            parameters["path"] = "desktop"
    
    # === SKILL ÇALIŞTIR ===
    if action not in ["small_talk", "unknown"]:
        perform_skill(action, parameters)
    
    # === HAFIZA'YA EKLE ===
    memory.add(user_input, reply)

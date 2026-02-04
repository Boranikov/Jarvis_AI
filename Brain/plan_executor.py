"""
Jarvis AI - Plan Executor
Reasoning Engine'den gelen çalıştırılabilir planları yürütür.
"""

from Skills.skills_manager import perform_skill
from config import DEBUG_MODE


def execute_plan(executable_steps: list) -> dict:
    """
    Çalıştırılabilir adımları sırayla yürütür.
    
    Args:
        executable_steps: [{"action": "...", "params": {...}}, ...] formatında adımlar
        
    Returns:
        {
            "success": bool,
            "total": int,
            "completed": int,
            "failed": int,
            "results": [{"step": int, "action": str, "success": bool, "error": str|None}, ...]
        }
    """
    if not executable_steps or not isinstance(executable_steps, list):
        return {
            "success": True,
            "total": 0,
            "completed": 0,
            "failed": 0,
            "results": []
        }
    
    results = []
    completed = 0
    failed = 0
    
    for i, step in enumerate(executable_steps, 1):
        action = step.get("action")
        params = step.get("params", {})
        
        if not action:
            results.append({
                "step": i,
                "action": None,
                "success": False,
                "error": "Aksiyon belirtilmemiş"
            })
            failed += 1
            continue
        
        # Params'ın dict olduğundan emin ol
        if not isinstance(params, dict):
            params = {}
        
        if DEBUG_MODE:
            print(f">> [PLAN] Adım {i}: {action} - Params: {params}")
        
        try:
            # Skill'i çalıştır
            success = perform_skill(action, params)
            
            if success:
                completed += 1
                results.append({
                    "step": i,
                    "action": action,
                    "success": True,
                    "error": None
                })
            else:
                failed += 1
                results.append({
                    "step": i,
                    "action": action,
                    "success": False,
                    "error": "Skill başarısız oldu"
                })
                
        except Exception as e:
            failed += 1
            results.append({
                "step": i,
                "action": action,
                "success": False,
                "error": str(e)
            })
            if DEBUG_MODE:
                print(f">> [PLAN ERROR] Adım {i}: {str(e)}")
    
    return {
        "success": failed == 0,
        "total": len(executable_steps),
        "completed": completed,
        "failed": failed,
        "results": results
    }


def format_execution_result(result: dict) -> str:
    """
    Plan yürütme sonucunu kullanıcıya gösterilecek formata çevir.
    
    Args:
        result: execute_plan sonucu
        
    Returns:
        Formatlanmış string
    """
    if result["total"] == 0:
        return ""
    
    total = result["total"]
    completed = result["completed"]
    
    if result["success"]:
        return f"\n✓ Tüm adımlar başarıyla tamamlandı ({completed}/{total})"
    else:
        failed = result["failed"]
        return f"\n⚠ {completed}/{total} adım tamamlandı, {failed} adım başarısız oldu"

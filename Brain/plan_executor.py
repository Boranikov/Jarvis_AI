"""
Jarvis AI - Plan Executor

Reasoning Engine'den gelen çalıştırılabilir planları yürütür.
"""

from typing import Any, Optional

from Skills.skills_manager import perform_skill
from Config.config import get_logger

logger = get_logger("brain.plan_executor")


def execute_plan(executable_steps: list[dict[str, Any]]) -> dict[str, Any]:
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
            "results": [{"step": int, "action": str, "success": bool, "error": str|None}]
        }
    """
    if not executable_steps or not isinstance(executable_steps, list):
        return {
            "success": True,
            "total": 0,
            "completed": 0,
            "failed": 0,
            "results": [],
        }

    results: list[dict[str, Any]] = []
    completed: int = 0
    failed: int = 0

    for i, step in enumerate(executable_steps, 1):
        action: Optional[str] = step.get("action")
        params: Any = step.get("params", {})

        if not action:
            results.append({
                "step": i,
                "action": None,
                "success": False,
                "error": "Aksiyon belirtilmemiş",
            })
            failed += 1
            continue

        # Params'ın dict olduğundan emin ol
        if not isinstance(params, dict):
            params = {}

        logger.debug("Adım %d: %s — Params: %s", i, action, params)

        try:
            success: bool = perform_skill(action, params)

            if success:
                completed += 1
                results.append({
                    "step": i,
                    "action": action,
                    "success": True,
                    "error": None,
                })
            else:
                failed += 1
                results.append({
                    "step": i,
                    "action": action,
                    "success": False,
                    "error": "Skill başarısız oldu",
                })

        except OSError as exc:
            failed += 1
            results.append({
                "step": i,
                "action": action,
                "success": False,
                "error": str(exc),
            })
            logger.error("Adım %d OS hatası: %s", i, exc)
        except Exception as exc:
            failed += 1
            results.append({
                "step": i,
                "action": action,
                "success": False,
                "error": str(exc),
            })
            logger.error("Adım %d beklenmeyen hata: %s", i, exc, exc_info=True)

    return {
        "success": failed == 0,
        "total": len(executable_steps),
        "completed": completed,
        "failed": failed,
        "results": results,
    }


def format_execution_result(result: dict[str, Any]) -> str:
    """
    Plan yürütme sonucunu kullanıcıya gösterilecek formata çevir.

    Args:
        result: execute_plan sonucu

    Returns:
        Formatlanmış string (boş string eğer çalıştırılacak adım yoksa)
    """
    total: int = result["total"]
    if total == 0:
        return ""

    completed: int = result["completed"]

    if result["success"]:
        return f"\n✓ Tüm adımlar başarıyla tamamlandı ({completed}/{total})"

    failed: int = result["failed"]
    return f"\n⚠ {completed}/{total} adım tamamlandı, {failed} adım başarısız oldu"

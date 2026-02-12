"""
Jarvis AI - Math Validator

LLM yanıtlarını numpy/sympy ile doğrular.
"""

import ast
import operator
import re
from typing import Any, Optional

from config import get_logger

logger = get_logger("utils.math_validator")

# Sympy ve numpy opsiyonel
try:
    import sympy as sp
    from sympy.parsing.sympy_parser import (
        parse_expr,
        standard_transformations,
        implicit_multiplication_application,
    )

    SYMPY_AVAILABLE: bool = True
except ImportError:
    SYMPY_AVAILABLE = False

try:
    import numpy as np

    NUMPY_AVAILABLE: bool = True
except ImportError:
    NUMPY_AVAILABLE = False


_SAFE_OPERATORS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
}


def _safe_eval(expr: str) -> float | int:
    """Güvenli aritmetik değerlendirme."""
    tree = ast.parse(expr, mode="eval")
    return _eval_node(tree.body)


def _eval_node(node: ast.AST) -> float | int:
    """AST node'unu güvenli şekilde değerlendir."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp):
        op_func = _SAFE_OPERATORS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Desteklenmeyen operatör: {type(node.op).__name__}")
        return op_func(_eval_node(node.left), _eval_node(node.right))
    elif isinstance(node, ast.UnaryOp):
        op_func = _SAFE_OPERATORS.get(type(node.op))
        if op_func is None:
            raise ValueError(f"Desteklenmeyen unary operatör: {type(node.op).__name__}")
        return op_func(_eval_node(node.operand))
    else:
        raise ValueError(f"Güvenli olmayan ifade: {ast.dump(node)}")


_EQUATION_KEYWORDS: frozenset[str] = frozenset({
    "çöz", "denklem", "kök", "değer", "x", "y",
})

_VARIABLE_CANDIDATES: tuple[str, ...] = ("x", "y", "z", "a", "b", "n")


def is_equation(text: str) -> bool:
    """Denklem olup olmadığını kontrol et."""
    text_lower: str = text.lower()
    if "=" in text and "==" not in text:
        return True
    return any(kw in text_lower for kw in _EQUATION_KEYWORDS)


def is_arithmetic(text: str) -> bool:
    """Basit aritmetik olup olmadığını kontrol et."""
    return bool(re.search(r"\d+\s*[\+\-\*\/\^\%]\s*\d+", text))


def extract_equation(text: str) -> Optional[str]:
    """Metinden denklemi çıkar."""
    match = re.search(r"([x-z0-9\+\-\*\/\^\=\s\(\)]+)", text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_arithmetic(text: str) -> Optional[str]:
    """Metinden aritmetik ifadeyi çıkar."""
    match = re.search(r"(\d+[\d\+\-\*\/\^\%\s\(\)\.]+\d+)", text)
    return match.group(1).strip() if match else None


def extract_numbers_from_response(text: str) -> list[str]:
    """Yanıttan sayıları çıkar."""
    return re.findall(r"-?\d+\.?\d*", text)


def is_number(s: str) -> bool:
    """String'in sayı olup olmadığını kontrol et."""
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def _solve_equation_with_sympy(expr_str: str) -> Optional[list]:
    """Denklemi sympy ile çöz."""
    if not SYMPY_AVAILABLE:
        return None

    # Değişkeni bul
    variable: str = "x"
    expr_lower: str = expr_str.lower()
    for var in _VARIABLE_CANDIDATES:
        if var in expr_lower:
            variable = var
            break

    x = sp.Symbol(variable)

    # = işaretini işle
    processed: str = expr_str
    if "=" in processed:
        parts: list[str] = processed.split("=")
        if len(parts) == 2:
            processed = f"({parts[0].strip()}) - ({parts[1].strip()})"

    # ^ → ** dönüşümü
    processed = processed.replace("^", "**")

    transformations = standard_transformations + (implicit_multiplication_application,)
    parsed = parse_expr(
        processed, local_dict={variable: x}, transformations=transformations
    )
    solutions = sp.solve(parsed, x)

    return solutions if solutions else None


def _format_solutions(solutions: list) -> str:
    """Sympy çözümlerini okunabilir stringe çevir."""
    formatted: list[str] = []
    for sol in solutions:
        if sol.is_real:
            val = sol.evalf()
            if val == int(val):
                formatted.append(str(int(val)))
            else:
                formatted.append(str(round(float(val), 4)))
        else:
            formatted.append(str(sol))
    return ", ".join(formatted)


def validate_math_response(user_input: str, llm_response: str) -> dict[str, Any]:
    """LLM'in matematik yanıtını doğrula."""
    result: dict[str, Any] = {
        "validated": False,
        "method": "none",
        "computed_result": None,
        "llm_result": None,
        "match": None,
        "note": None,
    }

    # Denklem mi?
    if is_equation(user_input):
        if SYMPY_AVAILABLE:
            return _validate_equation(user_input, llm_response)
        result["note"] = "sympy yüklü değil, doğrulama yapılamadı"
        return result

    # Aritmetik mi?
    if is_arithmetic(user_input):
        return _validate_arithmetic(user_input, llm_response)

    result["note"] = "Doğrulanabilir matematik ifadesi bulunamadı"
    return result


def _validate_equation(user_input: str, llm_response: str) -> dict[str, Any]:
    """Denklemi sympy ile doğrula."""
    result: dict[str, Any] = {
        "validated": False,
        "method": "sympy",
        "computed_result": None,
        "llm_result": None,
        "match": None,
        "note": None,
    }

    try:
        expr: Optional[str] = extract_equation(user_input)
        if not expr:
            result["note"] = "Denklem çıkarılamadı"
            return result

        solutions = _solve_equation_with_sympy(expr)
        if solutions is None:
            result["note"] = "Çözüm bulunamadı"
            return result

        result["computed_result"] = _format_solutions(solutions)
        result["validated"] = True

        # LLM yanıtından sonucu çıkar
        llm_numbers: list[str] = extract_numbers_from_response(llm_response)
        result["llm_result"] = ", ".join(llm_numbers) if llm_numbers else None

        # Eşleşme kontrolü
        if llm_numbers:
            match: bool = any(
                any(
                    abs(float(sol.evalf()) - float(n)) < 0.01
                    for n in llm_numbers
                    if is_number(n)
                )
                for sol in solutions
                if sol.is_real
            )
            result["match"] = match

    except (ValueError, TypeError, AttributeError) as exc:
        result["note"] = f"Doğrulama hatası: {str(exc)[:50]}"
    except Exception as exc:
        result["note"] = f"Doğrulama hatası: {str(exc)[:50]}"
        logger.error("Equation validation hatası: %s", exc, exc_info=True)

    return result


def _validate_arithmetic(user_input: str, llm_response: str) -> dict[str, Any]:
    """Basit aritmetiği güvenli parser ile doğrula."""
    result: dict[str, Any] = {
        "validated": False,
        "method": "numpy" if NUMPY_AVAILABLE else "python",
        "computed_result": None,
        "llm_result": None,
        "match": None,
        "note": None,
    }

    try:
        expr: Optional[str] = extract_arithmetic(user_input)
        if not expr:
            result["note"] = "Aritmetik ifade çıkarılamadı"
            return result

        # Operatör dönüşümleri
        expr = expr.replace("^", "**").replace("×", "*").replace("÷", "/")

        # Güvenli hesaplama (eval yerine AST-tabanlı parser)
        computed: float | int = _safe_eval(expr)

        # Sonucu formatla
        if isinstance(computed, float) and computed.is_integer():
            computed = int(computed)
        elif isinstance(computed, float):
            computed = round(computed, 6)

        result["computed_result"] = str(computed)
        result["validated"] = True

        # LLM yanıtından sonucu çıkar
        llm_numbers: list[str] = extract_numbers_from_response(llm_response)
        if llm_numbers:
            result["llm_result"] = llm_numbers[-1]
            result["match"] = str(computed) in llm_numbers

    except (ValueError, ZeroDivisionError) as exc:
        result["note"] = f"Hesaplama hatası: {str(exc)[:50]}"
    except Exception as exc:
        result["note"] = f"Hesaplama hatası: {str(exc)[:50]}"
        logger.error("Arithmetic validation hatası: %s", exc, exc_info=True)

    return result


def format_validation_result(validation: dict[str, Any]) -> str:
    """Doğrulama sonucunu formatla."""
    if not validation["validated"]:
        return ""

    if validation["match"] is True:
        return f"✓ Doğrulandı ({validation['method']}): {validation['computed_result']}"
    elif validation["match"] is False:
        return f"⚠ Hesaplanan: {validation['computed_result']} (farklılık olabilir)"
    else:
        return f"📊 Hesaplanan: {validation['computed_result']}"


_FAILURE_KEYWORDS: frozenset[str] = frozenset({
    "yapamıyorum", "çözemiyorum", "bilmiyorum", "emin değilim",
    "hesaplayamıyorum", "bulamıyorum", "anlayamıyorum",
    "karmaşık", "zor", "yardımcı olamıyorum",
    "mümkün değil", "başaramıyorum", "yetersiz",
    "hata", "sorun", "problem",
})


def llm_failed_to_solve(llm_response: str) -> bool:
    """LLM'in matematiği çözemediğini tespit et."""
    response_lower: str = llm_response.lower()
    return any(kw in response_lower for kw in _FAILURE_KEYWORDS)


def solve_directly(user_input: str) -> dict[str, Any]:
    """Sympy/güvenli parser ile direkt çöz."""
    result: dict[str, Any] = {
        "success": False,
        "result": None,
        "method": None,
        "explanation": None,
    }

    # Denklem mi?
    if is_equation(user_input):
        if not SYMPY_AVAILABLE:
            result["explanation"] = "Sympy yüklü değil, denklem çözülemiyor."
            return result

        try:
            expr: Optional[str] = extract_equation(user_input)
            if not expr:
                result["explanation"] = "Denklem ifadesi çıkarılamadı."
                return result

            # DRY: Ortak helper
            solutions = _solve_equation_with_sympy(expr)
            if solutions:
                # Değişkeni bul (debug mesajı için)
                variable: str = "x"
                for var in _VARIABLE_CANDIDATES:
                    if var in expr.lower():
                        variable = var
                        break

                result["success"] = True
                result["result"] = _format_solutions(solutions)
                result["method"] = "sympy"
                result["explanation"] = (
                    f"Denklemin çözümleri: {variable} = {result['result']}"
                )
            else:
                result["explanation"] = "Bu denklemin reel çözümü bulunamadı."

        except (ValueError, TypeError) as exc:
            result["explanation"] = f"Denklem çözme hatası: {str(exc)[:50]}"
        except Exception as exc:
            result["explanation"] = f"Denklem çözme hatası: {str(exc)[:50]}"
            logger.error("Doğrudan denklem çözme hatası: %s", exc, exc_info=True)

        return result

    # Aritmetik mi?
    if is_arithmetic(user_input):
        try:
            expr_str: Optional[str] = extract_arithmetic(user_input)
            if not expr_str:
                result["explanation"] = "Aritmetik ifade çıkarılamadı."
                return result

            expr_str = expr_str.replace("^", "**").replace("×", "*").replace("÷", "/")

            # Güvenli hesaplama
            computed: float | int = _safe_eval(expr_str)

            if isinstance(computed, float) and computed.is_integer():
                computed = int(computed)
            elif isinstance(computed, float):
                computed = round(computed, 6)

            result["success"] = True
            result["result"] = str(computed)
            result["method"] = "python"
            result["explanation"] = f"Hesaplama sonucu: {computed}"

        except (ValueError, ZeroDivisionError) as exc:
            result["explanation"] = f"Hesaplama hatası: {str(exc)[:50]}"
        except Exception as exc:
            result["explanation"] = f"Hesaplama hatası: {str(exc)[:50]}"
            logger.error("Doğrudan aritmetik çözme hatası: %s", exc, exc_info=True)

        return result

    result["explanation"] = "Matematik ifadesi tanınamadı."
    return result

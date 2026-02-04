"""
Jarvis AI - Math Validator
LLM yanıtlarını numpy/sympy ile doğrular.
Hibrit yaklaşım: LLM açıklar, bu modül doğrular.
"""

import re

# Sympy ve numpy opsiyonel
try:
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


def validate_math_response(user_input: str, llm_response: str) -> dict:
    """
    LLM'in matematik yanıtını doğrula.
    
    Args:
        user_input: Kullanıcının orijinal sorusu
        llm_response: LLM'in verdiği yanıt
        
    Returns:
        {
            "validated": bool,
            "method": "sympy" | "numpy" | "none",
            "computed_result": str | None,
            "llm_result": str | None,
            "match": bool | None,
            "note": str | None
        }
    """
    result = {
        "validated": False,
        "method": "none",
        "computed_result": None,
        "llm_result": None,
        "match": None,
        "note": None
    }
    
    # Denklem mi kontrol et
    if is_equation(user_input):
        if SYMPY_AVAILABLE:
            return validate_equation(user_input, llm_response)
        else:
            result["note"] = "sympy yüklü değil, doğrulama yapılamadı"
            return result
    
    # Basit aritmetik mi kontrol et
    if is_arithmetic(user_input):
        return validate_arithmetic(user_input, llm_response)
    
    result["note"] = "Doğrulanabilir matematik ifadesi bulunamadı"
    return result


def is_equation(text: str) -> bool:
    """Denklem olup olmadığını kontrol et."""
    text_lower = text.lower()
    if "=" in text and "==" not in text:
        return True
    equation_keywords = ["çöz", "denklem", "kök", "değer", "x", "y"]
    return any(kw in text_lower for kw in equation_keywords)


def is_arithmetic(text: str) -> bool:
    """Basit aritmetik olup olmadığını kontrol et."""
    # Sayı + operatör + sayı paterni
    return bool(re.search(r'\d+\s*[\+\-\*\/\^\%]\s*\d+', text))


def validate_equation(user_input: str, llm_response: str) -> dict:
    """Denklemi sympy ile doğrula."""
    result = {
        "validated": False,
        "method": "sympy",
        "computed_result": None,
        "llm_result": None,
        "match": None,
        "note": None
    }
    
    try:
        # Denklemi çıkar
        expr = extract_equation(user_input)
        if not expr:
            result["note"] = "Denklem çıkarılamadı"
            return result
        
        # Değişkeni bul
        variable = 'x'
        for var in ['x', 'y', 'z', 'a', 'b', 'n']:
            if var in expr.lower():
                variable = var
                break
        
        # Parse et
        x = sp.Symbol(variable)
        
        # = işaretini işle
        if "=" in expr:
            parts = expr.split("=")
            if len(parts) == 2:
                left = parts[0].strip()
                right = parts[1].strip()
                expr = f"({left}) - ({right})"
        
        # ^ -> ** dönüşümü
        expr = expr.replace("^", "**")
        
        # Sympy ile çöz
        transformations = standard_transformations + (implicit_multiplication_application,)
        parsed = parse_expr(expr, local_dict={variable: x}, transformations=transformations)
        solutions = sp.solve(parsed, x)
        
        if solutions:
            # Çözümleri basitleştir
            simplified = []
            for sol in solutions:
                # Karmaşık sayıları kontrol et
                if sol.is_real or (hasattr(sol, 'is_complex') and not sol.is_complex):
                    simplified.append(str(sol.evalf(4)))  # 4 basamak hassasiyet
                else:
                    simplified.append(str(sol))
            
            result["computed_result"] = ", ".join(simplified)
            result["validated"] = True
            
            # LLM yanıtından sonucu çıkarmaya çalış
            llm_numbers = extract_numbers_from_response(llm_response)
            result["llm_result"] = ", ".join(llm_numbers) if llm_numbers else None
            
            # Eşleşme kontrolü (basit)
            if llm_numbers:
                match = any(
                    any(abs(float(sol.evalf()) - float(n)) < 0.01 for n in llm_numbers if is_number(n))
                    for sol in solutions if sol.is_real
                )
                result["match"] = match
        else:
            result["note"] = "Çözüm bulunamadı"
            
    except Exception as e:
        result["note"] = f"Doğrulama hatası: {str(e)[:50]}"
    
    return result


def validate_arithmetic(user_input: str, llm_response: str) -> dict:
    """Basit aritmetiği doğrula."""
    result = {
        "validated": False,
        "method": "numpy" if NUMPY_AVAILABLE else "python",
        "computed_result": None,
        "llm_result": None,
        "match": None,
        "note": None
    }
    
    try:
        # Aritmetik ifadeyi çıkar
        expr = extract_arithmetic(user_input)
        if not expr:
            result["note"] = "Aritmetik ifade çıkarılamadı"
            return result
        
        # Güvenli hesaplama
        expr = expr.replace("^", "**")
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")
        
        # Hesapla
        computed = eval(expr, {"__builtins__": {}}, {})
        
        # Sonucu formatla
        if isinstance(computed, float):
            if computed.is_integer():
                computed = int(computed)
            else:
                computed = round(computed, 6)
        
        result["computed_result"] = str(computed)
        result["validated"] = True
        
        # LLM yanıtından sonucu çıkar
        llm_numbers = extract_numbers_from_response(llm_response)
        if llm_numbers:
            result["llm_result"] = llm_numbers[-1]  # Son sayı genellikle sonuç
            result["match"] = str(computed) in llm_numbers
        
    except Exception as e:
        result["note"] = f"Hesaplama hatası: {str(e)[:50]}"
    
    return result


def extract_equation(text: str) -> str:
    """Metinden denklemi çıkar."""
    # Basit denklem paterni
    match = re.search(r'([x-z0-9\+\-\*\/\^\=\s\(\)]+)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_arithmetic(text: str) -> str:
    """Metinden aritmetik ifadeyi çıkar."""
    # Sayı + operatör + sayı paterni
    match = re.search(r'(\d+[\d\+\-\*\/\^\%\s\(\)\.]+\d+)', text)
    if match:
        return match.group(1).strip()
    return None


def extract_numbers_from_response(text: str) -> list:
    """Yanıttan sayıları çıkar."""
    # Tam sayılar ve ondalıklı sayılar
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return numbers


def is_number(s: str) -> bool:
    """String'in sayı olup olmadığını kontrol et."""
    try:
        float(s)
        return True
    except:
        return False


def format_validation_result(validation: dict) -> str:
    """Doğrulama sonucunu formatla."""
    if not validation["validated"]:
        return ""
    
    if validation["match"] is True:
        return f"✓ Doğrulandı ({validation['method']}): {validation['computed_result']}"
    elif validation["match"] is False:
        return f"⚠ Hesaplanan: {validation['computed_result']} (farklılık olabilir)"
    else:
        return f"📊 Hesaplanan: {validation['computed_result']}"


def llm_failed_to_solve(llm_response: str) -> bool:
    """
    LLM'in matematiği çözemediğini tespit et.
    
    Args:
        llm_response: LLM'in yanıtı
        
    Returns:
        True eğer LLM yapamadığını söylüyorsa
    """
    failure_keywords = [
        "yapamıyorum", "çözemiyorum", "bilmiyorum", "emin değilim",
        "hesaplayamıyorum", "bulamıyorum", "anlayamıyorum",
        "karmaşık", "zor", "yardımcı olamıyorum",
        "mümkün değil", "başaramıyorum", "yetersiz",
        "hata", "sorun", "problem"
    ]
    
    response_lower = llm_response.lower()
    return any(kw in response_lower for kw in failure_keywords)


def solve_directly(user_input: str) -> dict:
    """
    Sympy/Numpy ile direkt çöz (LLM bypass).
    
    Args:
        user_input: Kullanıcının matematik sorusu
        
    Returns:
        {
            "success": bool,
            "result": str,
            "method": str,
            "explanation": str
        }
    """
    result = {
        "success": False,
        "result": None,
        "method": None,
        "explanation": None
    }
    
    # Denklem mi?
    if is_equation(user_input):
        if not SYMPY_AVAILABLE:
            result["explanation"] = "Sympy yüklü değil, denklem çözülemiyor."
            return result
        
        try:
            expr = extract_equation(user_input)
            if not expr:
                result["explanation"] = "Denklem ifadesi çıkarılamadı."
                return result
            
            # Değişkeni bul
            variable = 'x'
            for var in ['x', 'y', 'z', 'a', 'b', 'n']:
                if var in expr.lower():
                    variable = var
                    break
            
            x = sp.Symbol(variable)
            
            # = işaretini işle
            if "=" in expr:
                parts = expr.split("=")
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()
                    expr = f"({left}) - ({right})"
            
            expr = expr.replace("^", "**")
            
            transformations = standard_transformations + (implicit_multiplication_application,)
            parsed = parse_expr(expr, local_dict={variable: x}, transformations=transformations)
            solutions = sp.solve(parsed, x)
            
            if solutions:
                # Sonuçları formatla
                formatted = []
                for sol in solutions:
                    if sol.is_real:
                        val = sol.evalf()
                        if val == int(val):
                            formatted.append(str(int(val)))
                        else:
                            formatted.append(str(round(float(val), 4)))
                    else:
                        formatted.append(str(sol))
                
                result["success"] = True
                result["result"] = ", ".join(formatted)
                result["method"] = "sympy"
                result["explanation"] = f"Denklemin çözümleri: {variable} = {result['result']}"
            else:
                result["explanation"] = "Bu denklemin reel çözümü bulunamadı."
                
        except Exception as e:
            result["explanation"] = f"Denklem çözme hatası: {str(e)[:50]}"
        
        return result
    
    # Aritmetik mi?
    if is_arithmetic(user_input):
        try:
            expr = extract_arithmetic(user_input)
            if not expr:
                result["explanation"] = "Aritmetik ifade çıkarılamadı."
                return result
            
            expr = expr.replace("^", "**")
            expr = expr.replace("×", "*")
            expr = expr.replace("÷", "/")
            
            computed = eval(expr, {"__builtins__": {}}, {})
            
            if isinstance(computed, float):
                if computed.is_integer():
                    computed = int(computed)
                else:
                    computed = round(computed, 6)
            
            result["success"] = True
            result["result"] = str(computed)
            result["method"] = "python"
            result["explanation"] = f"Hesaplama sonucu: {computed}"
            
        except Exception as e:
            result["explanation"] = f"Hesaplama hatası: {str(e)[:50]}"
        
        return result
    
    result["explanation"] = "Matematik ifadesi tanınamadı."
    return result

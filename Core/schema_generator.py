import inspect
import typing
from typing import get_type_hints, Callable, Dict, Any, List

class SchemaGenerator:
    """
    Python fonksiyonlarını okuyarak OpenAI/Ollama formatında
    Native Tool (Function Calling) JSON şemaları üreten yardımcı sınıf.
    """

    # Python tipleri ile JSON Schema tipleri arasındaki haritalama
    TYPE_MAP = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        Any: "string", # Basitlik adına Any'i string kabul edelim.
    }

    @classmethod
    def generate_tool_schema(cls, func: Callable) -> Dict[str, Any]:
        """
        Verilen bir Python fonksiyonunu okur ve OpenAI/Ollama uyumlu
        'tools' objesi içindeki 'function' şemasını döner.
        """
        
        func_name = func.__name__
        
        # 1. Adım: Docstring'i (Açıklamayı) al ve temizle.
        docstring = inspect.getdoc(func)
        description = docstring.strip() if docstring else f"Function {func_name}"

        # 2. Adım: Parametre tiplerini ve isimlerini al.
        type_hints = get_type_hints(func)
        sig = inspect.signature(func)
        
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # 'self' parametresini atlıyoruz (eğer fonksiyon bir sınıf metoduyken çalıştırılırsa diye)
            if param_name == "self":
                continue

            # Default value (varsayılan değer) yoksa bu parametre zorunludur.
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

            # Tip ipucunu bul, yoksa default olarak 'str' kabul et.
            param_type = type_hints.get(param_name, str)
            
            # Type_map'ten JSON schema karşılığını bul
            json_type = cls.TYPE_MAP.get(param_type, "string")
            
            # Parametre açıklamasını docstring'den çekmeye çalış
            param_desc = f"The {param_name} parameter."
            if docstring:
                import re
                match = re.search(rf"{param_name}\b[^:]*:\s*([^\n]*)", docstring)
                if match:
                    param_desc = match.group(1).strip()
            
            properties[param_name] = {
                "type": json_type,
                "description": param_desc
            }

        # 3. Adım: Ollama/OpenAI standart formatında sözlüğü (dict) oluştur.
        schema = {
            "type": "function",
            "function": {
                "name": func_name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                }
            }
        }

        return schema

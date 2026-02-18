"""
Jarvis AI - Coding Engine

qwen2.5-coder:14b modeli ile kodlama, hata ayıklama ve proje yönetimi.
"""

import json
import re
from typing import Any, Optional

import ollama

from config import CODING_MODEL, get_logger
from Skills.skills_manager import perform_skill

logger = get_logger("brain.coding")

# Maksimum araç çağrısı döngüsü (sonsuz döngü koruması)
_MAX_TOOL_ITERATIONS: int = 10

# Yazma/silme işlemleri — kullanıcı onayı gerektirir
_DESTRUCTIVE_TOOLS: frozenset[str] = frozenset({
    "write_to_file", "delete_file",
})

SYSTEM_PROMPT: str = """
SEN: Jarvis'in Kıdemli Baş Yazılım Mühendisisin (Lead Software Engineer).
GÖREVİN: Kullanıcının projesini yönetmek, karmaşık kodlama isteklerini çözmek, hataları ayıklamak ve "Clean Code" prensiplerine uygun kod yazmak.
MODELİN: Qwen 2.5 Coder (14B). Zekanı ve mantığını tam kapasite kullan.

--- MEVCUT ARAÇLARIN (TOOLS) ---
Aşağıdaki araçları kullanarak dosya sistemiyle etkileşime geçersin:

1. `list_dir_recursive`
   - Amaç: Proje klasöründeki dosya ağacını görmek.
   - Ne Zaman Kullanılır: Hangi dosyaların var olduğunu bilmediğinde veya dosya yolunu doğrulamak için.
   - Parametre: {"path": "klasör_yolu"}

2. `read_file`
   - Amaç: Bir dosyanın TÜM içeriğini okumak.
   - Ne Zaman Kullanılır: Bir dosyayı değiştirmeden ÖNCE içeriğini görmek için.
   - Parametre: {"path": "klasör_yolu", "name": "dosya_adi"}

3. `write_to_file`
   - Amaç: Dosya oluşturmak veya mevcut dosyanın içeriğini GÜNCELLEMEK.
   - DİKKAT: Bu işlem dosyanın üzerine yazar (overwrite).
   - KURAL: Asla kodun bir kısmını yazıp "...geri kalanı aynı" deme. Dosyanın ÇALIŞIR HALDEKİ TAMAMINI yazmalısın.
   - Parametre: {"path": "klasör_yolu", "name": "dosya_adi", "content": "tam_kod_icerigi"}

4. `delete_file`
   - Amaç: Gereksiz veya hatalı dosyaları silmek.
   - Parametre: {"path": "klasör_yolu", "name": "dosya_adi"}

--- ÇALIŞMA PROTOKOLÜ (BU ADIMLARI ASLA ATLAMA) ---
1. ANALİZ ET: Kullanıcının isteğini anla.
2. KEŞFET (`list_dir_recursive`): Dosya yapısını bilmiyorsan önce listele. Ezbere dosya yolu uydurma.
3. OKU (`read_file`): Düzenleyeceğin dosyanın içeriğini MUTLAKA oku. İçeriği bilmeden kod yazmak YASAKTIR.
4. PLANLA: Yapacağın değişikliği düşün. Hangi kütüphaneler lazım? Nereyi değiştireceksin?
5. UYGULA (`write_to_file`): Kodu hatasız, eksiksiz ve tam olarak yaz.

--- ÇIKTI FORMATI (JSON) ---
Cevabın SADECE ve SADECE geçerli bir JSON objesi olmalıdır. Markdown, ```json``` etiketi veya ekstra metin kullanma.

Format Şablonu:
{
  "thought": "Buraya adım adım düşünce sürecini yaz. Neden bu aracı kullanıyorsun? Hedefin ne?",
  "tool": "read_file" | "write_to_file" | "list_dir_recursive" | "delete_file" | "final_answer",
  "args": {
      "path": "klasör_yolu",
      "name": "dosya_adi",
      "content": "kod..." (Sadece write_to_file için)
  },
  "response": "Kullanıcıya gösterilecek Türkçe mesaj (Sadece final_answer için)"
}

--- ÖRNEKLER ---

Örnek 1 (Keşif):
{
  "thought": "Kullanıcı login hatasından bahsetti ama hangi dosyada olduğunu bilmiyorum. Önce dosyaları listelemeliyim.",
  "tool": "list_dir_recursive",
  "args": {"path": "C:\\\\Users\\\\boran\\\\Desktop\\\\Jarvis_Aİ"}
}

Örnek 2 (Okuma):
{
  "thought": "main.py dosyasını buldum. İçindeki hatayı görmek için içeriğini okumalıyım.",
  "tool": "read_file",
  "args": {"path": "C:\\\\Users\\\\boran\\\\Desktop\\\\Jarvis_Aİ", "name": "main.py"}
}

Örnek 3 (Yazma):
{
  "thought": "main.py içindeki bug'ı tespit ettim. Düzeltilmiş ve TAM kodu yazıyorum.",
  "tool": "write_to_file",
  "args": {"path": "C:\\\\Users\\\\boran\\\\Desktop\\\\Jarvis_Aİ", "name": "main.py", "content": "import os\\n\\ndef login():\\n    print('Fixed')"}
}

Örnek 4 (Bitiş):
{
  "thought": "Tüm işlemleri tamamladım.",
  "tool": "final_answer",
  "args": {},
  "response": "Login fonksiyonundaki hatayı düzelttim ve gereksiz importları kaldırdım Efendim."
}

Sadece JSON ile yanıt ver, başka açıklama ekleme.
"""


def _call_model(messages: list[dict]) -> dict[str, Any]:
    """Coding modeline tek bir istek gönder ve JSON parse et."""
    try:
        response = ollama.chat(
            model=CODING_MODEL,
            messages=messages,
            options={"temperature": 0.2},
        )

        content: str = response.message.content.strip()
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            logger.warning("Coding JSON bulunamadı, ham yanıt: %.200s", content)
            return {"tool": "final_answer", "response": content, "args": {}}

        return json.loads(match.group())

    except json.JSONDecodeError as exc:
        logger.error("Coding JSON parse hatası: %s", exc)
        return {"tool": "final_answer", "response": "JSON parse hatası oluştu Efendim.", "args": {}}
    except ConnectionError as exc:
        logger.error("Ollama bağlantı hatası: %s", exc)
        return {"tool": "final_answer", "response": "Model bağlantısı kurulamadı Efendim.", "args": {}}
    except Exception as exc:
        logger.error("Coding Engine hatası: %s", exc, exc_info=True)
        return {"tool": "final_answer", "response": "Bir hata oluştu Efendim.", "args": {}}


def _execute_tool(tool_name: str, args: dict[str, Any]) -> str:
    """Araç çağrısını çalıştır ve sonucu string olarak döndür."""
    result = perform_skill(tool_name, args)

    if isinstance(result, bool):
        return "İşlem başarılı." if result else "İşlem başarısız."
    if isinstance(result, str):
        return result
    return str(result)


def process_coding_task(
    user_input: str,
    file_context: str = "",
    confirm_fn: Optional[callable] = None,
) -> dict[str, Any]:
    """
    Kodlama isteğini agentic döngü ile işler.

    Model, dosya okuma/yazma/listeleme araçlarını çağırarak
    kendi kendine görev tamamlama döngüsü çalıştırır.

    Args:
        user_input: Kullanıcı girdisi
        file_context: Ek bağlam bilgisi (opsiyonel)
        confirm_fn: Yazma/silme onayı için callback (opsiyonel).
                     None ise CLI'da input() ile sorulur.

    Returns:
        {"success": bool, "response": str, "actions_taken": list}
    """
    # Mesaj geçmişi (model hafızası)
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # İlk kullanıcı prompt'u
    prompt: str = f"KULLANICI İSTEĞİ: {user_input}\n"
    if file_context:
        prompt += f"\nGENEL BAĞLAM:\n{file_context}\n"
    messages.append({"role": "user", "content": prompt})

    actions_taken: list[dict] = []
    final_response: str = ""

    for iteration in range(_MAX_TOOL_ITERATIONS):
        logger.debug("Coding döngü iterasyonu: %d", iteration + 1)

        result: dict = _call_model(messages)
        tool: str = result.get("tool", "final_answer")
        args: dict = result.get("args", {})
        thought: str = result.get("thought", "")

        if thought:
            logger.debug("Düşünce: %s", thought[:150])

        # --- final_answer: Döngüyü bitir ---
        if tool == "final_answer":
            final_response = result.get("response", "İşlem tamamlandı Efendim.")
            break

        # --- Yıkıcı işlemler: Onay iste ---
        if tool in _DESTRUCTIVE_TOOLS:
            # Onay bilgisi hazırla
            file_name: str = args.get("name", "bilinmeyen")
            content_preview: str = ""
            if tool == "write_to_file":
                full_content = args.get("content", "")
                content_preview = full_content[:300]
                if len(full_content) > 300:
                    content_preview += "\n... (devamı var)"

            # Onay mekanizması
            approved: bool = False
            if confirm_fn:
                approved = confirm_fn(tool, file_name, content_preview)
            else:
                # CLI varsayılan onay
                print(f"\n{'='*50}")
                print(f"Jarvis [{tool}] → {file_name}")
                if content_preview:
                    print(f"İçerik önizleme:\n{content_preview}")
                print(f"{'='*50}")
                user_confirm: str = input("Onaylıyor musunuz? (E/H): ").strip().lower()
                approved = user_confirm in ("e", "evet", "y", "yes")

            if not approved:
                # Reddedildi — modele bildir ve devam et
                messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})
                messages.append({"role": "user", "content": "KULLANICI BU İŞLEMİ REDDETTİ. Başka bir yol dene veya final_answer ile bitir."})
                actions_taken.append({"tool": tool, "args": args, "status": "rejected"})
                continue

        # --- Aracı çalıştır ---
        tool_output: str = _execute_tool(tool, args)
        actions_taken.append({"tool": tool, "args": args, "status": "executed", "output_preview": tool_output[:200]})

        logger.debug("Araç sonucu [%s]: %.200s", tool, tool_output)

        # Model'e sonucu geri gönder (conversation devam etsin)
        messages.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})
        messages.append({"role": "user", "content": f"ARAÇ SONUCU ({tool}):\n{tool_output}\n\nDevam et. Bir sonraki adımın ne?"})

    else:
        # Döngü limiti aşıldı
        logger.warning("Coding döngüsü maksimum iterasyona ulaştı (%d)", _MAX_TOOL_ITERATIONS)
        final_response = "Maksimum adım sayısına ulaşıldı Efendim. Yapılan işlemler kaydedildi."

    return {
        "success": True,
        "response": final_response,
        "actions_taken": actions_taken,
    }
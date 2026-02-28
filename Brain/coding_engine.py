"""
Jarvis AI - Coding Engine

qwen2.5-coder:14b modeli ile kodlama, hata ayıklama ve proje yönetimi.
"""

import json
from typing import Any, Optional

import ollama

from config import CODING_MODEL, get_logger, MAX_TOOL_ITERATIONS, SAFETY_MODE
from Skills.skills_manager import perform_skill

logger = get_logger("brain.coding")

_DESTRUCTIVE_TOOLS: frozenset[str] = frozenset({"write_to_file", "delete_file"})
_DEFAULT_PROJECT_PATH: str = "Desktop"

SYSTEM_PROMPT: str = """
SEN: Jarvis'in Kıdemli Baş Yazılım Mühendisisin (Lead Software Engineer).
GÖREVİN: Kullanıcının kodlama isteklerini çözmek, proje oluşturmak, hataları ayıklamak ve tam çalışan kod yazmak.
MODELİN: Qwen 2.5 Coder (14B).
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
{{{{
  "thought": "...",
  "tool": "write_to_file",
  "args": {{...}},
  "response": "Sadece final_answer için"
}}}}

--- ÖRNEKLER ---

Kullanıcı: "Masaüstüne hesap-makinesi adında klasör oluştur içine main.py yaz"

Adım 1:
{{"thought": "Önce hesap-makinesi klasörünü oluşturup main.py dosyasını yazmalıyım.", "tool": "write_to_file", "args": {{"path": "{default_path}\\\\hesap-makinesi", "name": "main.py", "content": "def toplama(a, b):\\n    return a + b\\n\\ndef cikarma(a, b):\\n    return a - b\\n\\nif __name__ == '__main__':\\n    print(toplama(5, 3))"}}, "response": null}}

Adım 2 (araç sonucu aldıktan sonra):
{{"thought": "main.py başarıyla oluşturuldu. İşlem tamamlandı.", "tool": "final_answer", "args": {{}}, "response": "Hesap makinesi projesini oluşturdum Efendim. main.py dosyası hazır."}}

---

Kullanıcı: "config.py dosyasındaki hatayı bul"

Adım 1:
{{"thought": "Önce config.py dosyasının içeriğini okumam gerekiyor.", "tool": "read_file", "args": {{"path": "{default_path}\\\\Jarvis_Aİ", "name": "config.py"}}, "response": null}}

Adım 2 (dosya içeriğini aldıktan sonra):
{{"thought": "Hatayı tespit ettim: satır 15'te import yanlış yazılmış. Düzeltilmiş halini yazıyorum.", "tool": "write_to_file", "args": {{"path": "{default_path}\\\\Jarvis_Aİ", "name": "config.py", "content": "...düzeltilmiş tam kod..."}}, "response": null}}

Adım 3:
{{"thought": "Hata düzeltildi.", "tool": "final_answer", "args": {{}}, "response": "config.py dosyasındaki import hatasını düzelttim Efendim."}}

Sadece JSON ile yanıt ver.
""".format(default_path=_DEFAULT_PROJECT_PATH)



def _call_model(messages: list[dict]) -> dict[str, Any]:
    """Coding modeline istek gönder ve JSON parse et."""
    try:
        response = ollama.chat(
            model=CODING_MODEL,
            messages=messages,
            format="json",
            options={"temperature": 0.2},
        )

        return json.loads(response.message.content)

    except ConnectionError as exc:
        logger.error("Ollama bağlantı hatası: %s", exc)
        return {"tool": "final_answer", "response": "Model bağlantısı kurulamadı Efendim.", "args": {}}
    except json.JSONDecodeError as exc:
        logger.error("JSON parse hatası (format=json ile olmamali): %s", exc)
        return {"tool": "final_answer", "response": "Bir hata oluştu Efendim.", "args": {}}
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

    for iteration in range(MAX_TOOL_ITERATIONS):
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
        if SAFETY_MODE and tool in _DESTRUCTIVE_TOOLS:
            # Onay bilgisi hazırla
            file_name: str = args.get("name", "bilinmeyen")
            content_preview: str = ""
            if tool == "write_to_file":
                full_content = args.get("content", "")
                content_preview = full_content[:500]
                if len(full_content) > 500:
                    content_preview += "\n... (devamı var)"

            # Onay mekanizması
            approved: bool = False
            if confirm_fn:
                approved = confirm_fn(tool, file_name, content_preview)
            else:
                # CLI varsayılan onay
                print(f"\n{'='*60}")
                print(f"  Jarvis [{tool}] → {file_name}")
                print(f"{'='*60}")
                if content_preview:
                    print(f"{content_preview}")
                    print(f"{'='*60}")
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
        messages.append({
            "role": "user",
            "content": (
                f"ARAÇ SONUCU ({tool}):\n{tool_output}\n\n"
                "Bir sonraki adımına geç. Cevabın SADECE JSON olsun."
            ),
        })

    else:
        # Döngü limiti aşıldı
        logger.warning("Coding döngüsü maksimum iterasyona ulaştı (%d)", MAX_TOOL_ITERATIONS)
        final_response = "Maksimum adım sayısına ulaşıldı Efendim. Yapılan işlemler kaydedildi."

    return {
        "success": True,
        "response": final_response,
        "actions_taken": actions_taken,
    }
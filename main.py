from brain.intent_engine import process_command
from brain.memory import Memory
from Skills.skills_manager import perform_skill

memory = Memory()

PRESENCE_TRIGGERS = [
    "jarvis orda mısın",
    "jarvis orada mısın",
    "hey jarvis orda mısın",
    "hey jarvis orada mısın"
]

REQUIRED_PARAMS = {
    "create_file": ["name"],
    "create_folder": ["name"],
    "delete_file": ["name"],
    "delete_folder": ["name"]
}

MISSING_QUESTIONS = {
    "create_file": {
        "name": "Efendim, dosyanın ismini söyler misiniz?"
    },
    "create_folder": {
        "name": "Efendim, klasörün ismini söyler misiniz?"
    },
    "delete_file": {
        "name": "Efendim, silinecek dosyanın ismini belirtir misiniz?"
    },
    "delete_folder": {
        "name": "Efendim, silinecek klasörün ismini belirtir misiniz?"
    }
}

print("------------------------------------------------")
print("                  Jarvis")
print("------------------------------------------------")

while True:
    user_input = input("\nSen: ").strip()

    if user_input.lower() in ["çık", "exit"]:
        break

    if not user_input:
        continue

    normalized = user_input.lower()

    # --- HARD CODED PRESENCE ---
    if any(t in normalized for t in PRESENCE_TRIGGERS):
        print("Jarvis: Sizin için her zaman buradayım efendim.")
        continue

    # --- BEKLEYEN İŞLEM VAR MI? ---
    if memory.has_pending():
        completed = memory.fill_pending(user_input)
        if completed:
            action, params = completed
            print("Jarvis: İşleminiz tamamlanıyor efendim.")
            perform_skill(action, params)
        else:
            print("Jarvis: Devam edebilirsiniz efendim.")
        continue

    # --- INTENT ENGINE ---
    result = process_command(user_input, memory.history)

    action = result.get("action", "unknown")
    reply = result.get("reply", "Efendim?")
    params = result.get("parameters", {})

    print(f"Jarvis: {reply}")

    # --- EKSİK PARAMETRE YÖNETİMİ ---
    if action == "missing_parameters":
        original_action = result.get("original_action")
        missing = params.get("missing", [])

        if original_action and missing:
            memory.set_pending(original_action, missing)
            question = MISSING_QUESTIONS.get(
                original_action, {}
            ).get(missing[0], "Devam edebilmem için bilgi verir misiniz efendim?")
            print(f"Jarvis: {question}")
        continue

    # --- GÜVENLİK: EKSİK PARAMETRE VAR MI ---
    if action in REQUIRED_PARAMS:
        missing = [p for p in REQUIRED_PARAMS[action] if not params.get(p)]
        if missing:
            memory.set_pending(action, missing)
            question = MISSING_QUESTIONS[action][missing[0]]
            print(f"Jarvis: {question}")
            continue

    # --- SKILL ÇALIŞTIR ---
    if action not in ["small_talk", "unknown"]:
        perform_skill(action, params)

    # --- HAFIZA ---
    memory.add(user_input, reply)

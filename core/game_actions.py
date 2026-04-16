from core.state_manager import (
    unlock_document,
    add_item,
    add_knowledge_flag,
)

def handle_action(action: str, player_state: dict):
    action = action.strip().lower()
    if action == "reset inventory":
        player_state["inventory"] = []
        return "Inventory has been cleared."

    elif action == "inventory":
        items = player_state.get("inventory", [])
        if not items:
            return "Inventory is empty."
        return "Inventory: " + ", ".join(items)

    if action == "inspect desk":
        unlock_document(player_state, "doc_002")
        add_knowledge_flag(player_state, "suspects_logs_were_altered")
        return "You inspect the desk and recover a handwritten warning."

    elif action == "search generator room":
        unlock_document(player_state, "doc_001")
        add_knowledge_flag(player_state, "knows_generator_failed")
        return "You search the generator room and find a maintenance log."

    elif action == "open locker":
        add_item(player_state, "red_keycard")
        return "You open the locker and obtain a red keycard."

    elif action == "check state":
        return f"Current state: {player_state}"

    else:
        return "Nothing changes. That action yields no useful result."
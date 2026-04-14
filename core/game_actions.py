from core.state_manager import (
    unlock_document,
    add_item,
    add_knowledge_flag,
    load_player_state,
)


def handle_action(action: str):
    action = action.strip().lower()

    if action == "inspect desk":
        unlock_document("doc_002")
        add_knowledge_flag("suspects_logs_were_altered")
        return "You inspect the desk and recover a handwritten warning."

    elif action == "search generator room":
        unlock_document("doc_001")
        add_knowledge_flag("knows_generator_failed")
        return "You search the generator room and find a maintenance log."

    elif action == "open locker":
        add_item("red_keycard")
        return "You open the locker and obtain a red keycard."

    elif action == "check state":
        state = load_player_state()
        return f"Current state: {state}"

    else:
        return "Nothing changes. That action yields no useful result."
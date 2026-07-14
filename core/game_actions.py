import json
from pathlib import Path
from core.state_manager import (
    unlock_document,
    add_item,
    add_knowledge_flag,
    change_stage,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_PATH = BASE_DIR / "data" / "documents.json"

with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
    DOCUMENTS = json.load(f)

HELP_TEXT = """
Available commands:
- look around
- inspect <object>
- search <place>
- open <object>
- take <item>
- use <item>
- unlock <object>
- inventory
- documents
- state
- help

If a line is not an action command, ORION treats it as a question.
""".strip()

ROOM_DESCRIPTION = """
You stand in a damaged research wing. Emergency lights pulse over a desk, a sealed locker, a terminal, and a corridor door. A sign points toward the generator room. The final exit is still deeper inside: Whisper Gate.
""".strip()


def _has_item(player_state: dict, item_name: str) -> bool:
    return item_name in player_state.get("inventory", [])


def _has_flag(player_state: dict, flag: str) -> bool:
    return flag in player_state.get("knowledge_flags", [])


def _format_documents(player_state: dict) -> str:
    unlocked_ids = set(player_state.get("documents_unlocked", []))
    visible_docs = [doc for doc in DOCUMENTS if doc["id"] in unlocked_ids]

    if not visible_docs:
        return "No documents recovered yet."

    lines = ["Recovered documents:"]
    for doc in visible_docs:
        lines.append(f"- {doc['title']}: {doc['content']}")
    return "\n".join(lines)


def handle_action(action: str, player_state: dict):
    action = action.strip().lower()

    if action == "help":
        return HELP_TEXT

    if action == "look around":
        add_knowledge_flag(player_state, "surveyed_research_wing")
        return ROOM_DESCRIPTION

    if action == "inventory":
        items = player_state.get("inventory", [])
        if not items:
            return "Inventory is empty."
        return "Inventory: " + ", ".join(items)

    if action == "documents":
        return _format_documents(player_state)

    if action == "state":
        return f"Current state: {player_state}"

    if action in {"inspect desk", "search desk"}:
        unlock_document(player_state, "doc_002")
        add_knowledge_flag(player_state, "suspects_logs_were_altered")
        return "You inspect the desk and recover a handwritten warning about altered terminal outputs."

    if action in {"inspect terminal", "use terminal", "open terminal", "search terminal"}:
        if _has_flag(player_state, "suspects_logs_were_altered"):
            unlock_document(player_state, "doc_003")
            add_knowledge_flag(player_state, "found_conflicting_security_summary")
            return "The terminal produces a security summary. Its timestamp falls after 02:13, making it suspect."
        return "The terminal is active, but its records are difficult to trust without more context."

    if action in {"search generator room", "inspect generator room"}:
        unlock_document(player_state, "doc_001")
        add_knowledge_flag(player_state, "knows_generator_failed")
        return "You search the generator room and find a maintenance log about the backup generator failure."

    if action in {"open locker", "inspect locker", "search locker"}:
        add_item(player_state, "red_keycard")
        return "You open the locker and obtain a red keycard."

    if action == "take keycard":
        add_item(player_state, "red_keycard")
        return "You take the red keycard."

    if action in {"use keycard", "use red_keycard", "use red keycard"}:
        if not _has_item(player_state, "red_keycard"):
            return "You do not have a keycard to use."
        add_knowledge_flag(player_state, "keycard_ready")
        return "The red keycard is ready. Use it on a locked door or unlock the door."

    if action in {"unlock door", "unlock corridor door", "open door", "open corridor door"}:
        if not _has_item(player_state, "red_keycard"):
            return "The corridor door remains locked. A compatible keycard is required."
        change_stage(player_state, max(player_state.get("stage", 1), 2))
        add_knowledge_flag(player_state, "corridor_unlocked")
        return "The red keycard unlocks the corridor door. Stage 2 access is now available."

    if action in {"unlock whisper gate", "open whisper gate", "use keycard on whisper gate"}:
        required_flags = {
            "knows_generator_failed",
            "suspects_logs_were_altered",
            "found_conflicting_security_summary",
        }
        if player_state.get("stage", 1) < 2:
            return "Whisper Gate is beyond the locked corridor. You cannot reach it yet."
        if not required_flags.issubset(set(player_state.get("knowledge_flags", []))):
            return "Whisper Gate refuses the attempt. You still lack enough evidence to judge the records."
        change_stage(player_state, 3)
        add_knowledge_flag(player_state, "whisper_gate_ready")
        return "Whisper Gate accepts your evidence chain. The final threshold is ready."

    return "Nothing changes. That action yields no useful result."

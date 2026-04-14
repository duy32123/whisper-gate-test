import json


PLAYER_STATE_PATH = "state/player_state.json"


def load_player_state():
    with open(PLAYER_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_player_state(player_state):
    with open(PLAYER_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(player_state, f, indent=2)


def unlock_document(doc_id: str):
    player_state = load_player_state()

    if doc_id not in player_state["documents_unlocked"]:
        player_state["documents_unlocked"].append(doc_id)

    save_player_state(player_state)


def add_item(item_name: str):
    player_state = load_player_state()

    if item_name not in player_state["inventory"]:
        player_state["inventory"].append(item_name)

    save_player_state(player_state)


def add_knowledge_flag(flag: str):
    player_state = load_player_state()

    if flag not in player_state["knowledge_flags"]:
        player_state["knowledge_flags"].append(flag)

    save_player_state(player_state)


def change_stage(new_stage: int):
    player_state = load_player_state()
    player_state["stage"] = new_stage
    save_player_state(player_state)


def change_trust(delta: int):
    player_state = load_player_state()
    player_state["trust_level"] += delta

    if player_state["trust_level"] < 0:
        player_state["trust_level"] = 0

    save_player_state(player_state)
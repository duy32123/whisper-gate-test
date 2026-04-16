import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PLAYER_STATE_PATH = BASE_DIR / "state" / "player_state.json"

def load_initial_state():
    with open(PLAYER_STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def unlock_document(player_state, doc_id: str):
    if doc_id not in player_state["documents_unlocked"]:
        player_state["documents_unlocked"].append(doc_id)

def add_item(player_state, item_name: str):
    if item_name not in player_state["inventory"]:
        player_state["inventory"].append(item_name)

def add_knowledge_flag(player_state, flag: str):
    if flag not in player_state["knowledge_flags"]:
        player_state["knowledge_flags"].append(flag)

def change_stage(player_state, new_stage: int):
    player_state["stage"] = new_stage

def change_trust(player_state, delta: int):
    player_state["trust_level"] += delta
    if player_state["trust_level"] < 0:
        player_state["trust_level"] = 0
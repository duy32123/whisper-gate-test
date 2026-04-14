print("PARSER VERSION: loaded")

def parse_action(user_input: str):
    text = user_input.strip().lower()

    if any(phrase in text for phrase in ["inspect desk", "search desk", "look at desk", "check desk"]):
        return "inspect desk"

    if any(phrase in text for phrase in ["search generator room", "inspect generator room", "check generator room"]):
        return "search generator room"

    if any(phrase in text for phrase in ["open locker", "check locker", "inspect locker"]):
        return "open locker"

    if text in {"check state", "show state", "status"}:
        return "check state"

    return None
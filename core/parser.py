COMMAND_VERBS = {
    "look",
    "inspect",
    "search",
    "open",
    "take",
    "use",
    "unlock",
}

INFORMATION_COMMANDS = {
    "inventory",
    "documents",
    "state",
    "help",
}

ALIASES = {
    "look": "look around",
    "look around": "look around",
    "look room": "look around",
    "look at room": "look around",
    "check state": "state",
    "show state": "state",
    "status": "state",
    "show inventory": "inventory",
    "bag": "inventory",
    "show documents": "documents",
    "docs": "documents",
    "document": "documents",
    "commands": "help",
    "?": "help",
}


def parse_action(user_input: str):
    text = " ".join(user_input.strip().lower().split())

    if not text:
        return None

    if text in ALIASES:
        return ALIASES[text]

    if text in INFORMATION_COMMANDS:
        return text

    for verb in COMMAND_VERBS:
        if text == verb or text.startswith(f"{verb} "):
            return text

    return None

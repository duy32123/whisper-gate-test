from ai.llm_handler import generate_response
from core.game_actions import handle_action
from core.parser import parse_action

print("APP VERSION: parser-enabled")

def main():
    print("Whisper Gate Core is online.")
    print("Type a question to ask the AI, or type an action.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Whisper Gate Core: Session terminated.")
            break

        if not user_input:
            continue

        parsed_action = parse_action(user_input)

        if parsed_action is not None:
            result = handle_action(parsed_action)
            print(f"System: {result}\n")
        else:
            answer = generate_response(user_input)
            print(f"Whisper Gate Core: {answer}\n")

if __name__ == "__main__":
    main()
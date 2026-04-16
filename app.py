import streamlit as st

from ai.llm_handler import generate_response
from core.game_actions import handle_action
from core.parser import parse_action
from core.state_manager import load_initial_state

st.set_page_config(page_title="Whisper Gate", page_icon="🧠", layout="wide")

def init_app():
    if "player_state" not in st.session_state:
        st.session_state.player_state = load_initial_state()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Whisper Gate Core is online.\n\n"
                    "Ask the AI a question, or enter an action like "
                    "`inspect desk`, `open locker`, `search generator room`."
                )
            }
        ]

init_app()

st.title("Whisper Gate")

with st.sidebar:
    st.subheader("Player State")
    st.json(st.session_state.player_state)

    if st.button("Reset game"):
        st.session_state.player_state = load_initial_state()
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Session reset. Whisper Gate Core is online again."
            }
        ]
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask the AI or enter an action...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    parsed_action = parse_action(user_input)

    if parsed_action is not None:
        reply = handle_action(parsed_action, st.session_state.player_state)
    else:
        reply = generate_response(user_input, st.session_state.player_state)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
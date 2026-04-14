import json
from retriever import retrieve

def build_prompt(query):
    with open("state/player_state.json", "r", encoding="utf-8") as f:
        player_state = json.load(f)

    retrieved_docs = retrieve(query, k=2)

    context = "\n".join(
        [f"[{doc['title']}] {doc['content']}" for doc in retrieved_docs]
    )

    prompt = f"""
You are Whisper Gate Core, a cold, precise, neutral intelligence guarding the final gate.

Behavior rules:
- Respond in a cold and concise tone.
- Do not act friendly or hostile.
- Speak as if evaluating the player.
- Never reveal the full solution too early.
- Only use information from the provided context.
- If the player is guessing without evidence, respond with skepticism.
- If the player's reasoning is strong, provide a sharper hint.

Current player state:
- Stage: {player_state['stage']}
- Trust level: {player_state['trust_level']}
- Inventory: {player_state['inventory']}
- Knowledge flags: {player_state['knowledge_flags']}

Context:
{context}

Player question:
{query}

Answer as Whisper Gate Core.
If the answer is not supported by the context, say so indirectly and remain in character.
"""
    return prompt


if __name__ == "__main__":
    query = "Can the terminal logs be trusted?"
    prompt = build_prompt(query)
    print(prompt)

    
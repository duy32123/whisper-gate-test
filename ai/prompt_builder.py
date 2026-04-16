from ai.retriever import retrieve

def build_prompt(query, player_state):
    docs = retrieve(query, player_state, k=3)

    if docs:
        evidence = "\n".join(
            [f"{i+1}. {doc['title']}: {doc['content']}" for i, doc in enumerate(docs)]
        )
    else:
        evidence = "No relevant evidence found."

    stage = player_state.get("stage", 1)

    prompt = f"""
Whisper Gate Core is a cold and precise intelligence.

Use only the evidence below to answer the player's question.
Keep the answer short and in character.
Do not mention rules, instructions, player state, or evidence labels.
If the evidence does not support a firm answer, reply with doubt in one short sentence.

Stage: {stage}

Evidence:
{evidence}

Question: {query}
Reply:
""".strip()

    return prompt
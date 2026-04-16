import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from ai.prompt_builder import build_prompt

BANNED_PREFIXES = [
    "if the evidence",
    "do not mention",
    "use only the evidence",
    "reply:",
    "question:",
    "stage:",
    "trust level:",
    "inventory:",
    "knowledge flags:",
]

@st.cache_resource
def load_llm():
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
    return tokenizer, model

def sanitize_answer(answer: str) -> str:
    text = answer.strip()
    low = text.lower()

    for bad in BANNED_PREFIXES:
        if low.startswith(bad):
            return "The record is compromised. Do not accept it at face value."

    return text

def generate_response(query: str, player_state: dict, max_new_tokens: int = 48):
    tokenizer, model = load_llm()
    prompt = build_prompt(query, player_state)

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        num_beams=4,
        repetition_penalty=1.15,
        no_repeat_ngram_size=3
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sanitize_answer(answer)
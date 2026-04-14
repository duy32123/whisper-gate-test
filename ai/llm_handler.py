from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from ai.prompt_builder import build_prompt

# Load model once
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")


def generate_response(query: str, max_new_tokens: int = 80):
    prompt = build_prompt(query)

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens
    )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer


if __name__ == "__main__":
    query = "Can the terminal logs be trusted?"
    answer = generate_response(query)

    print("Question:", query)
    print("\nAnswer:")
    print(answer)
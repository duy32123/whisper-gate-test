import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PLAYER_STATE = {
    "stage": 1,
    "trust_level": 0,
    "inventory": [],
    "documents_unlocked": [],
    "knowledge_flags": [],
}

RUNTIME_DEPS: dict[str, Any] = {}


def load_runtime_dependencies() -> tuple[Any, Any]:
    if "generate_response" in RUNTIME_DEPS and "retrieve" in RUNTIME_DEPS:
        return RUNTIME_DEPS["generate_response"], RUNTIME_DEPS["retrieve"]

    try:
        from ai.llm_handler import generate_response
        from ai.retriever import retrieve
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing runtime dependency. Install project requirements (e.g. streamlit, transformers, sentence-transformers, scikit-learn) before running eval."
        ) from exc

    RUNTIME_DEPS["generate_response"] = generate_response
    RUNTIME_DEPS["retrieve"] = retrieve
    return generate_response, retrieve


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSONL at line {line_number} in {path}: {exc}"
                ) from exc

    return rows


def tokenize(text: str) -> set[str]:
    lowered = text.lower()
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in lowered)
    return {token for token in cleaned.split() if token}


def overlap_ratio(a: str, b: str) -> float:
    ta = tokenize(a)
    tb = tokenize(b)
    if not ta or not tb:
        return 0.0
    intersection = ta.intersection(tb)
    union = ta.union(tb)
    return len(intersection) / len(union)


def score_answer(question: str, answer: str, contexts: list[str], ground_truth: str | None) -> dict[str, Any]:
    relevance_value = overlap_ratio(question, answer)
    if relevance_value >= 0.20:
        relevance = 2
    elif relevance_value >= 0.08:
        relevance = 1
    else:
        relevance = 0

    context_joined = "\n".join(contexts)
    groundedness_value = overlap_ratio(answer, context_joined)
    if groundedness_value >= 0.22:
        groundedness = 2
    elif groundedness_value >= 0.10:
        groundedness = 1
    else:
        groundedness = 0

    context_utilization = groundedness

    if ground_truth:
        correctness_value = overlap_ratio(answer, ground_truth)
        if correctness_value >= 0.22:
            correctness = 2
        elif correctness_value >= 0.10:
            correctness = 1
        else:
            correctness = 0
    else:
        correctness_value = None
        correctness = -1

    insufficient_context = len(contexts) == 0
    if insufficient_context:
        caution_markers = [
            "insufficient",
            "incomplete",
            "cannot confirm",
            "not enough",
            "missing",
            "uncertain",
            "conflict",
        ]
        low_answer = answer.lower()
        if any(marker in low_answer for marker in caution_markers):
            safety = 2
        elif len(tokenize(answer)) <= 12:
            safety = 1
        else:
            safety = 0
    else:
        safety = 2 if groundedness >= 1 else 1

    hallucination = groundedness == 0 and len(tokenize(answer)) > 4

    return {
        "relevance": relevance,
        "relevance_value": round(relevance_value, 4),
        "groundedness": groundedness,
        "groundedness_value": round(groundedness_value, 4),
        "correctness": correctness,
        "correctness_value": round(correctness_value, 4) if correctness_value is not None else None,
        "context_utilization": context_utilization,
        "safety_insufficient_context": safety,
        "hallucination": hallucination,
    }


def run_sample(sample: dict[str, Any], top_k: int, max_new_tokens: int) -> dict[str, Any]:
    generate_response, retrieve = load_runtime_dependencies()

    sample_id = sample["id"]
    question = sample["question"]
    player_state = sample.get("player_state", DEFAULT_PLAYER_STATE)

    retrieved_docs = retrieve(question, player_state, k=top_k)
    retrieved_ids = [doc["id"] for doc in retrieved_docs]
    contexts = [f"{doc['title']}. {doc['content']}" for doc in retrieved_docs]

    model_answer = generate_response(
        query=question,
        player_state=player_state,
        max_new_tokens=max_new_tokens,
    )

    ground_truth = sample.get("ground_truth_answer")
    scores = score_answer(question, model_answer, contexts, ground_truth)

    gold_doc_ids = set(sample.get("gold_doc_ids", []))
    if gold_doc_ids:
        hits = len(gold_doc_ids.intersection(set(retrieved_ids)))
        retrieval_recall = hits / len(gold_doc_ids)
    else:
        retrieval_recall = None

    return {
        "id": sample_id,
        "question": question,
        "ground_truth_answer": ground_truth,
        "gold_doc_ids": list(gold_doc_ids),
        "retrieved_doc_ids": retrieved_ids,
        "retrieved_contexts": contexts,
        "model_answer": model_answer,
        "retrieval_recall_at_k": retrieval_recall,
        "scores": scores,
    }


def average(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def build_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    recall_values = [
        row["retrieval_recall_at_k"]
        for row in results
        if row["retrieval_recall_at_k"] is not None
    ]

    relevance_values = [row["scores"]["relevance"] for row in results]
    groundedness_values = [row["scores"]["groundedness"] for row in results]
    correctness_values = [
        row["scores"]["correctness"]
        for row in results
        if row["scores"]["correctness"] >= 0
    ]
    context_util_values = [row["scores"]["context_utilization"] for row in results]

    hallucinations = [row["scores"]["hallucination"] for row in results]
    hallucination_rate = round(sum(1 for h in hallucinations if h) / len(hallucinations), 4)

    return {
        "num_samples": len(results),
        "retrieval_recall_at_k": average(recall_values),
        "answer_relevance_avg": average(relevance_values),
        "groundedness_avg": average(groundedness_values),
        "correctness_avg": average(correctness_values),
        "context_utilization_avg": average(context_util_values),
        "hallucination_rate": hallucination_rate,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run eval for Whisper Gate RAG pipeline.")
    parser.add_argument("--dataset", type=Path, required=True, help="Path to JSONL eval dataset.")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON result path.")
    parser.add_argument("--top-k", type=int, default=3, help="Top-k documents for retrieval.")
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=48,
        help="Max new tokens for generator output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    dataset = load_jsonl(args.dataset)
    results: list[dict[str, Any]] = []

    for sample in dataset:
        if "id" not in sample or "question" not in sample:
            raise ValueError("Each sample must contain 'id' and 'question'.")
        results.append(run_sample(sample, top_k=args.top_k, max_new_tokens=args.max_new_tokens))

    payload = {
        "summary": build_summary(results),
        "samples": results,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[eval] Wrote results to: {args.output}")
    print("[eval] Summary:")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

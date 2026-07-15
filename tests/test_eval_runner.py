import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_PATH = REPO_ROOT / "eval" / "run_eval.py"

spec = importlib.util.spec_from_file_location("run_eval", MODULE_PATH)
run_eval = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(run_eval)


def test_load_jsonl_reads_rows(tmp_path):
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text(
        "\n".join(
            [
                json.dumps({"id": "q1", "question": "What happened?"}),
                json.dumps({"id": "q2", "question": "Can I trust logs?"}),
            ]
        ),
        encoding="utf-8",
    )

    rows = run_eval.load_jsonl(dataset)

    assert len(rows) == 2
    assert rows[0]["id"] == "q1"
    assert rows[1]["question"] == "Can I trust logs?"


def test_overlap_ratio_nonzero_for_shared_terms():
    ratio = run_eval.overlap_ratio("generator failed in sector b", "sector b backup generator failed")
    assert ratio > 0


def test_score_answer_handles_missing_ground_truth():
    scores = run_eval.score_answer(
        question="Who altered the records?",
        answer="The record is incomplete.",
        contexts=["Handwritten Warning. Someone altered the logs."],
        ground_truth=None,
    )

    assert scores["correctness"] == -1
    assert isinstance(scores["hallucination"], bool)


def test_build_summary_computes_expected_fields():
    sample_results = [
        {
            "retrieval_recall_at_k": 1.0,
            "scores": {
                "relevance": 2,
                "groundedness": 2,
                "correctness": 2,
                "context_utilization": 2,
                "hallucination": False,
            },
        },
        {
            "retrieval_recall_at_k": 0.0,
            "scores": {
                "relevance": 1,
                "groundedness": 1,
                "correctness": 0,
                "context_utilization": 1,
                "hallucination": True,
            },
        },
    ]

    summary = run_eval.build_summary(sample_results)

    assert summary["num_samples"] == 2
    assert summary["retrieval_recall_at_k"] == 0.5
    assert summary["hallucination_rate"] == 0.5
    assert "answer_relevance_avg" in summary

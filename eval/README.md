# Evaluation Scaffold

Thư mục này chứa khung đánh giá (eval) cho pipeline RAG của Whisper Gate.

## Mục tiêu

- Đo chất lượng retrieval.
- Đo chất lượng câu trả lời của model.
- Theo dõi hallucination / mức độ bám theo context.

## Cấu trúc

- `dataset_template.jsonl`: Mẫu dataset eval.
- `rubric.md`: Rubric chấm điểm chi tiết.
- `run_eval.py`: Script chạy eval end-to-end.
- `results/`: Nơi lưu kết quả JSON.

## Cách dùng nhanh

```bash
python eval/run_eval.py --dataset eval/dataset_template.jsonl --output eval/results/baseline.json
```

## Định dạng dataset

Mỗi dòng là một JSON object (JSONL) với các trường:

- `id` (bắt buộc): mã mẫu eval
- `question` (bắt buộc): câu hỏi đưa vào model
- `player_state` (tùy chọn): state riêng cho sample
- `ground_truth_answer` (tùy chọn): đáp án chuẩn để so correctness
- `gold_doc_ids` (tùy chọn): doc id chuẩn để tính retrieval recall@k

Nếu `player_state` bị bỏ trống, script dùng state mặc định:

```json
{
  "stage": 1,
  "trust_level": 0,
  "inventory": [],
  "documents_unlocked": [],
  "knowledge_flags": []
}
```

## Output

Script tạo JSON gồm:

- `summary`: metric tổng hợp
- `samples`: chi tiết từng câu

Metric có sẵn:

- `retrieval_recall_at_k`
- `answer_relevance_avg`
- `groundedness_avg`
- `correctness_avg`
- `context_utilization_avg`
- `hallucination_rate`

## Lưu ý

- Bộ chấm hiện tại dùng heuristic để bạn chạy được ngay không cần API ngoài.
- Khi cần độ chính xác cao hơn, bạn có thể thay phần `score_answer(...)` bằng LLM-as-judge.

## Chạy test trên GitHub

Repo đã có GitHub Actions workflow tại `.github/workflows/eval-ci.yml` để tự chạy:

- unit tests cho `eval/run_eval.py`
- smoke test CLI `python eval/run_eval.py --help`

Vì vậy bạn có thể kiểm tra kết quả trực tiếp trong tab **Actions** trên GitHub sau khi push/PR.

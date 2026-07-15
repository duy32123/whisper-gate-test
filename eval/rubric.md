# RAG Evaluation Rubric

Mỗi mẫu được chấm theo thang **0-2** cho từng tiêu chí.

## 1) Answer Relevance
- **2**: Trả lời trực tiếp, đúng trọng tâm câu hỏi.
- **1**: Có liên quan nhưng thiếu ý/chưa rõ.
- **0**: Lạc đề hoặc không trả lời.

## 2) Groundedness / Faithfulness
- **2**: Các ý chính đều bám vào context retrieve được.
- **1**: Đa phần bám context nhưng có vài ý suy diễn nhẹ.
- **0**: Có nhiều nội dung không có trong context (hallucination).

## 3) Correctness (nếu có ground truth)
- **2**: Đúng hoàn toàn.
- **1**: Đúng một phần.
- **0**: Sai nội dung chính.

## 4) Context Utilization
- **2**: Tận dụng thông tin quan trọng từ context.
- **1**: Có dùng context nhưng hời hợt.
- **0**: Gần như không dùng context.

## 5) Safety under Insufficient Context
- **2**: Biết từ chối/suy luận thận trọng khi thiếu dữ kiện.
- **1**: Có cảnh báo nhưng vẫn đoán nhẹ.
- **0**: Bịa thông tin khi thiếu context.

---

## Điều kiện pass gợi ý

- `answer_relevance_avg >= 1.6`
- `groundedness_avg >= 1.5`
- `hallucination_rate <= 0.10`

Bạn có thể chỉnh ngưỡng theo độ khó và domain.

# Bài làm Part 7

## 7.1 Metrics

Counter: `http_requests_total`; Gauge: `agent_in_flight_requests`; Histogram: `http_request_duration_seconds`. Đã thêm histogram `agent_question_length_chars`, observe trước retrieval/LLM. Dùng route template và nhãn `unmatched` tránh tạo một time series mới cho mỗi đường dẫn ngẫu nhiên do bot quét.

Đã gửi câu hỏi `Hello`: `/metrics` trả `agent_question_length_chars_count 1` và `agent_question_length_chars_sum 5`.

## 7.2–7.3 Load test và eval

Các số đo, giới hạn của lần chạy và liên kết báo cáo JSON ở [báo cáo tại gốc repo](../../BENCHMARK_REPORT.md). Workflow `.github/workflows/eval.yml` chạy v2 với error rate 0 và yêu cầu accuracy ít nhất 85%.

## 7.4–7.7

Đã kiểm tra metrics qua Prometheus, trace lỗi và trace chậm qua Jaeger API, hai alert firing và scaling Locust; chi tiết ở [báo cáo tại gốc repo](../../BENCHMARK_REPORT.md). Có ảnh Grafana khi tải đang chạy, trace lỗi mở exception và alert firing. Chưa xác nhận trace chậm nhất trong UI.

# Benchmark & Observability Report — Day 14

**Họ tên:** Đặng Quang Duy

**Ngày chạy:** 26/11/2026

**Môi trường:** Docker Desktop trên Windows, agent mock. Các số dưới đây là từng lần chạy, không phải trung bình nhiều lần. Các phép đo develop đặt `MOCK_ERROR_RATE=0`; phép đo production sử dụng lỗi mock theo cấu hình của từng thử nghiệm.

## SLO

Load test develop dùng ngưỡng p95 ≤ 500 ms và error rate ≤ 2% theo script; quality gate yêu cầu accuracy ≥ 85%. Các ngưỡng này giúp phát hiện latency đuôi, lỗi thường xuyên và suy giảm chất lượng. Không xem một lần chạy là bằng chứng về SLO dài hạn.

## Load test develop

300 request mỗi lần, slow rate mặc định 0,03, SLO p95 ≤ 500 ms và lỗi ≤ 2% theo script.

| Concurrency | RPS | p50 ms | p95 ms | p99 ms | Lỗi | SLO |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 3,63 | 200,8 | 328,8 | 1721,5 | 0% | Pass |
| 10 | 38,97 | 202,7 | 259,0 | 1700,2 | 0% | Pass |
| 50 | 39,94 | 454,3 | 3599,9 | 5208,9 | 0% | Fail p95 |
| 100 | 44,07 | 1294,8 | 5759,2 | 6515,8 | 0% | Fail p95 |

Với concurrency 20: slow rate 0 cho avg/p95/p99 = 214,3/275,5/335,2 ms; slow rate 0,03 cho 248,6/327,3/1731,2 ms; slow rate 0,1 cho 401,5/1715,8/1744,6 ms. Tail latency làm p95/p99 tăng rõ; trung bình có thể che mất request chậm. Các file [JSON](reports/) chứa kết quả các lần chạy lại; đây là các lần đo riêng, không trực tiếp so sánh với số đo trước. Stack observability vẫn chạy trên cùng máy trong lần đo lại. RPS tăng không tuyến tính; ở tải cao p95 tăng mạnh, nhưng một lần chạy không đủ xác định nút thắt cụ thể.

## Eval

| Phiên bản | Accuracy | Avg tokens | Tổng cost | Gate |
|---|---:|---:|---:|---|
| v1 | 1/23 (4,3%) | 57,2 | $0,000406 | Fail |
| v2 trước bổ sung HPA và JWT | 21/23 (91,3%) | 109,0 | $0,000759 | Pass theo ngưỡng 80% |
| v2 sau bổ sung HPA và JWT | 23/23 (100%) | 113,7 | $0,000790 | Pass, 0 regression |

Chi tiết và cách chấm ở `reports/eval_v1.json`, `reports/eval_v2.json` và `reports/eval_v2_fixed.json`. Baseline v2 được dựng lại sau đó bằng cách loại hai mục vừa bổ sung khỏi knowledge base; `security-02` thiếu token, hết hạn và chữ ký, còn `scaling-03` thiếu CPU, memory và custom metrics. So sánh với baseline v2: cải thiện hai câu và không regression. Chất lượng tăng nhưng token và chi phí tăng trong lần đo này.

## Observability production

Ban đầu agent không khởi động do package cài dưới `/home/agent/.local` nhưng thiếu `PYTHONUSERBASE`; đã sửa Dockerfile. Sau đó Prometheus scrape được hai agent, `/health` qua Nginx trả 200 và `/metrics` qua Nginx trả 404 theo cấu hình bảo vệ. `promtool test rules` trả SUCCESS.

Truy vấn Prometheus khi đang chạy tải 30 users và 3 instance (dữ liệu [JSON](reports/prometheus_queries.json)): p95 `/ask` 292,8 ms, avg 216,0 ms; p95 cao hơn cho thấy phần request chậm hơn trung bình. Tốc độ `/ask` theo ba instance lần lượt khoảng 6,24, 6,31 và 6,22 request/s, gần đều trong khoảng đo một phút. Input khoảng 1073 token/s, output khoảng 570 token/s; input bao gồm system prompt, câu hỏi và tài liệu retrieval nên lớn hơn. `GET /metrics` qua Nginx trả 404 vì chỉ Prometheus được scrape trực tiếp trong mạng nội bộ.

| Thử nghiệm | Kết quả |
|---|---|
| Pause một agent | Lần thử lại: lệnh pause hoàn tất khoảng 11:35:54 UTC; `AgentInstanceDown` pending tại lần kiểm tra 11:36:28 và firing tại 11:36:34, tức khoảng 34–40 giây sau pause. Quy tắc yêu cầu 30 giây pending. |
| `MOCK_ERROR_RATE=0.2`, Locust 30 users | Lần thử lại: cấu hình hoàn tất khoảng 11:37:29 UTC; `AgentHighErrorRate` pending lúc 11:38:40, firing lúc 11:38:46 với error rate khoảng 20,6%, tức khoảng 71–77 giây sau cập nhật. Tải bắt đầu lúc 11:37:38; quy tắc yêu cầu 1 phút pending. |

Trace lỗi `72c0de8f524f49d2d77bfa83b8d25997` được tìm từ log `llm_error` rồi đọc qua Jaeger API: span `chat mock-llm-small` có sự kiện `exception` và trạng thái lỗi. JSON trace và các trạng thái alert nằm trong `reports/trace_error.json`, `alerts_instance_down.json` và `alerts_error_timed.json`.

Một trace chậm được tìm trong log có ID `bd056a20bdd2e20faf82b4aefacc3f7c`: span HTTP 1759,3 ms, `agent.run` 1672,0 ms, `chat mock-llm-small` 1654,4 ms, retrieval 17,3 ms. Đây là một trace chậm quan sát được, không khẳng định là trace chậm nhất. Dữ liệu gốc: `reports/trace_slow.json`.

Chuyển sang v1 có thể làm chất lượng giảm mà metrics hệ thống vẫn bình thường; phát hiện bằng eval trên golden dataset, quality gate, và kiểm tra chất lượng trên mẫu traffic thật. Ảnh: [Grafana khi có tải](screenshots/grafana-dashboard.png), [trace chậm](screenshots/jaeger-slow-trace.png), [trace lỗi và exception](screenshots/jaeger-error-trace.png), [alert firing](screenshots/prometheus-alert-firing.png). Error rate cao trong ảnh Grafana là do thử nghiệm lỗi giả lập.

## Scaling production

Locust headless, 100 users, ramp 10/s, 2 phút; các số dưới đây chỉ cho `POST /ask`, trích CSV trong `benchmark-results/`.

| Instance | RPS | p50 ms | p95 ms | p99 ms | Lỗi |
|---:|---:|---:|---:|---:|---:|
| 1 | 59,04 | 200 | 620 | 1700 | 75/7069 |
| 3 | 60,11 | 190 | 240 | 1700 | 83/7189 |

Trong hai lần đo này, p95 giảm nhưng RPS gần như không đổi; p99 vẫn phản ánh độ trễ mock. Chưa đủ bằng chứng để xác định nút thắt. Các lỗi 503 phù hợp cơ chế lỗi ngẫu nhiên mặc định của mock. CSV `baseline_*` có giai đoạn agent lỗi khởi động nên không dùng làm baseline sạch.

## Kết luận

Percentile cho thấy các request chậm mà số trung bình có thể che khuất. Eval bắt lỗi chất lượng không nhất thiết làm tăng error rate. Metrics, logs và traces bổ sung cho nhau khi xác định bước gây lỗi hoặc chậm; hai lần scale này chưa đủ để kết luận nguyên nhân giới hạn throughput. Khi vận hành thật cần giám sát thêm chất lượng theo tập đánh giá, Redis readiness và chi phí theo khoảng thời gian, với ngưỡng được chọn từ yêu cầu thực tế.

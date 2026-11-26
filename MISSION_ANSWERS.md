# Day 14 — Mission Answers

## Part 1 — Localhost và production

Trong bản basic có hardcode API key và database URL, log API key, cấu hình cố định, dùng `print`, không có health check, cố định port, chỉ bind localhost và bật reload. Xem phân tích và bảng so sánh tại [bài làm Part 1](01-localhost-vs-production/BAI_LAM_1.1-1.3.md). Bản basic nhận `question` qua query string, nên JSON body trong đề trả 422; query hợp lệ trả 200. Bản advanced có env config, health/readiness và lifecycle nhưng vẫn có hạn chế được nêu trong bài làm.

## Part 2 — Docker

Base image basic là `python:3.11`, working directory `/app`. Copy requirements trước giúp tận dụng cache. `CMD` cung cấp lệnh mặc định, `ENTRYPOINT` xác định chương trình chính. Image basic và advanced được Docker inspect báo lần lượt 426.319.951 và 57.409.042 byte; advanced nhỏ hơn khoảng 86,5% theo cùng phép đo. Stack agent, Redis, Qdrant và Nginx đã chạy và trả 200 qua Nginx. Chi tiết tại [bài làm Part 2](02-docker/BAI_LAM.md).

## Part 3 — Cloud

Đã deploy lên Render: [URL service](https://k5-l3b-day14-dangquangduy-2a202603984.onrender.com/). Railway không thực hiện được do tài khoản bị giới hạn; người học chọn Render để đáp ứng yêu cầu có ít nhất một nền tảng. So sánh Render và Railway tại [bài làm Part 3](03-cloud-deployment/BAI_LAM.md). Cloud Run là tùy chọn.

## Part 4 — API security

API key basic: thiếu/sai/đúng key lần lượt trả 401/403/200. JWT: `/auth/token` phát token; người dùng `student` gọi `/ask` thành công. Sliding window cho user 10 request/phút: kiểm thử 10 lần 200, lần 11 trả 429. Hàm cost guard tháng dùng Redis Lua để kiểm tra và đặt trước chi phí nguyên tử; các khoản 6, 4 và 0,01 USD lần lượt trả `True`, `True`, `False`. Hàm này là bài tập độc lập, chưa nối vào `/ask` của ví dụ Part 4. Chi tiết tại [bài làm Part 4](04-api-gateway/BAI_LAM.md).

## Part 5 — Scaling và reliability

`/health` và `/ready` bản develop trả 200; gửi SIGTERM khi request mock đang chạy, request trả 200 và process thoát mã 0. Ở bản production, session dùng Redis thay vì fallback memory và cập nhật message nguyên tử bằng Lua. Kiểm thử ba instance: năm request đi qua cả ba, history có 10 message; sau khi dừng một agent, cùng session tiếp tục hoạt động. Chi tiết và hạn chế tại [bài làm Part 5](05-scaling-reliability/BAI_LAM.md).

## Part 6 — Production readiness

Đã chạy đầy đủ `check_production_ready.py` trong container có Docker CLI, Redis tạm và quyền Docker. Phần checklist trong output:

```text
✅ Dockerfile (multi-stage, < 500 MB)
✅ docker-compose.yml (agent + redis)
✅ .dockerignore
✅ Health check endpoint (GET /health)
✅ Readiness endpoint (GET /ready)
✅ API Key authentication
✅ Rate limiting
✅ Cost guard
✅ Config từ environment variables
✅ Structured logging
✅ Graceful shutdown
✅ Public URL ready (Railway / Render config)
Result: 12/12 tiêu chí đạt · 42/42 checks passed
PASS 12/12
```

Image theo script: 56 MB; Docker stop thoát mã 0 trong 0,5 giây. Các số là kết quả thực nghiệm ngày 26/11/2026. Public service Render đã được kiểm tra `/health`, `/ready`, `/ask` thiếu key và người học kiểm tra `/ask` với key hợp lệ.

## AI log

- Người học yêu cầu Codex hoàn thành và kiểm tra các exercise, chuẩn bị deployment và bài nộp. Codex phân tích mã, tạo câu trả lời Part 1–5, triển khai Part 6 và Part 7, thực hiện kiểm thử HTTP, Docker, Redis, benchmark, eval và observability.
- Người học tự tạo Key Value, cấu hình và deploy service Render; tự chạy kiểm tra `/ask` có key và chụp ảnh observability. Chưa ghi nhận việc người học tự sửa mã. Người học cần đọc lại và có thể giải thích mọi đoạn mã, số đo và kết quả trước khi nộp.
- Các phép đo, dữ liệu và giới hạn được ghi trong [BENCHMARK_REPORT.md](BENCHMARK_REPORT.md). Railway chưa thực hiện do giới hạn tài khoản; không tạo số đo hay deployment giả.

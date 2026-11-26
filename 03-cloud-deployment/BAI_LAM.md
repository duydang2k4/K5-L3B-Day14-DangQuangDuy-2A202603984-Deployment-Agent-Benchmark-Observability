# Bài làm Part 3

## Render

Ngày 26/11/2026 kiểm tra deployment do người học cung cấp: `https://k5-l3b-day14-dangquangduy-2a202603984.onrender.com/`.

Exercise 3.1 Railway không thực hiện được vì tài khoản Railway của người học bị giới hạn; người học chọn Render để đáp ứng checkpoint deploy tối thiểu một nền tảng.

- `GET /health`: HTTP 200, `status: ok`.
- `POST /ask` với JSON `{"question":"Hello"}`: thành công, trả câu hỏi và câu trả lời mock.
- Response ghi `platform: Railway` vì ứng dụng trong `railway/app.py` gán cứng chuỗi này; hostname và header phản hồi xác nhận request đi tới Render. Đây là nhãn trong code, không phải xác định nền tảng tự động.

## So sánh cấu hình

`railway.toml` khai báo builder Nixpacks, start command, health check và chính sách restart cho Railway; biến môi trường được thiết lập riêng. `render/render.yaml` khai báo dịch vụ web, runtime Python, region, plan, build/start command, health check và biến môi trường, đồng thời khai báo dịch vụ Redis. Cả hai đều dùng `$PORT` và `/health`. File Render trong thư mục ví dụ không tự chứng minh cấu hình đang chạy trên dashboard.

Exercise 3.3 (Cloud Run) là tùy chọn và chưa thực hiện.

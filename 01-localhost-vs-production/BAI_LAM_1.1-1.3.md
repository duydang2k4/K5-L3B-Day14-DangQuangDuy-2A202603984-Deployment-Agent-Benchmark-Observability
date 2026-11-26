# Bài làm Exercise 1.1–1.3

## 1.1. Anti-patterns trong bản basic

1. API key và thông tin kết nối database được ghi cứng trong mã nguồn; nếu đưa mã lên Git, thông tin có thể bị lộ và khó thay đổi theo môi trường. Các giá trị trong ví dụ là giả.
2. API key còn được in ra log khi gọi `/ask`, làm tăng nguy cơ lộ bí mật.
3. Cấu hình như `DEBUG` và `MAX_TOKENS` được ghi cứng, khó thay đổi giữa development và production.
4. Dùng `print()` cho log, không có cấu trúc hoặc mức độ log để dễ lọc và giám sát.
5. Không có endpoint health check hoặc readiness để hệ thống triển khai kiểm tra trạng thái.
6. Port 8000 được ghi cứng, không dùng biến `PORT` do nền tảng cấp.
7. Server chỉ bind `localhost`, nên không nhận kết nối từ bên ngoài container hoặc máy chủ.
8. `reload=True` bật cơ chế tự tải lại phục vụ phát triển; không phù hợp khi chạy production.
9. Không định nghĩa lifecycle để dọn dẹp tài nguyên khi tắt. Uvicorn vẫn có cơ chế shutdown riêng; không thể kết luận mọi request đều bị ngắt đột ngột chỉ từ mã này.

## 1.2. Chạy bản basic

Endpoint basic khai báo `question: str` là query parameter. Do đó lệnh JSON trong CODE_LAB sẽ nhận lỗi 422 vì thiếu query parameter; lệnh đúng là:

```powershell
cd 01-localhost-vs-production/develop
pip install -r requirements.txt
python app.py
# Trong terminal khác:
curl.exe -X POST "http://localhost:8000/ask?question=Hello"
```

Kết quả mong đợi là HTTP 200 và JSON có trường `answer` chứa một câu trả lời mock. Bản chạy được vẫn chưa production-ready vì các vấn đề ở mục 1.1.

**Kết quả thực nghiệm (26/11/2026):** Chạy `python app.py` trong Docker bằng image `agent-develop:latest` có FastAPI 0.115.0 và Uvicorn 0.30.0. Gửi JSON theo CODE_LAB trả HTTP **422**, với lỗi thiếu `query.question`; gửi `POST /ask?question=Hello` trả HTTP **200** và trường `answer` chứa câu trả lời mock. Trong phiên làm việc kiểm tra, lệnh `python` trỏ tới một virtual environment của dự án khác và không chạy được; điều này không kết luận Python trên máy host bị lỗi.

## 1.3. So sánh basic và advanced

| Feature | Basic | Advanced | Tại sao quan trọng? |
|---|---|---|---|
| Config | Ghi cứng trong `app.py` | `config.py` đọc biến môi trường với giá trị mặc định | Dễ cấu hình theo môi trường và tránh ghi secret thật trong mã. |
| Health check | Không có | `/health` và `/ready`; readiness dựa trên cờ khởi tạo | Giúp hệ thống phân biệt tiến trình còn sống và ứng dụng sẵn sàng nhận traffic. |
| Logging | `print()`, có in API key | Dùng `logging`, định dạng hướng JSON và không log key trong endpoint | Hỗ trợ lọc, phân tích log và giảm lộ bí mật. |
| Shutdown | Không có cleanup riêng | Có lifecycle startup/shutdown và handler SIGTERM; Uvicorn quản lý vòng đời server | Cho phép ứng dụng dọn dẹp tài nguyên khi dừng. |
| Mạng | `localhost:8000` cố định | `HOST` mặc định `0.0.0.0`, port lấy từ `PORT` | Cho phép truy cập qua container và tương thích port do cloud cấp. |
| Request `/ask` | Query parameter `question` | JSON body `{"question": "Hello"}` | Cần dùng đúng hợp đồng API của từng phiên bản. |

Lưu ý: bản advanced là ví dụ minh họa, chưa nên mặc định xem là production-ready. Formatter log ghép chuỗi JSON thủ công nên các message chứa dấu nháy có thể làm dòng log không phải JSON hợp lệ; readiness chỉ kiểm tra cờ nội bộ, không kiểm tra dependency. Handler SIGTERM chỉ ghi log; hành vi hoàn tất request phụ thuộc Uvicorn và cần kiểm thử thực tế. Ngoài ra `config.py` dùng `os.getenv` nhưng không gọi `load_dotenv`, nên chỉ sao chép `.env` chưa tự nạp biến khi chạy `python app.py`.

Để chạy bản advanced trên PowerShell, có thể nạp các biến cần thiết vào môi trường trước khi chạy:

```powershell
cd 01-localhost-vs-production/production
pip install -r requirements.txt
$env:PORT = '8000'
$env:ENVIRONMENT = 'development'
python app.py
# Trong terminal khác:
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
curl.exe -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{\"question\":\"Hello\"}'
```

**Kết quả thực nghiệm (26/11/2026):** Chạy `python app.py` của bản advanced trong cùng image Docker, với `PORT=8000` và `DEBUG=false`. `GET /health` trả HTTP **200** và `status: ok`; `GET /ready` trả HTTP **200** và `ready: true`; `POST /ask` với JSON `{"question":"Hello"}` trả HTTP **200**, gồm `question`, `answer` mock và `model: gpt-4o-mini`. Các kiểm tra này xác nhận khởi động và phản hồi HTTP, chưa kiểm chứng hoàn tất request đang xử lý khi shutdown.

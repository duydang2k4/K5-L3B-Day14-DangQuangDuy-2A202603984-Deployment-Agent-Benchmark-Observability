# Bài làm Part 5

## 5.1–5.2 Health và shutdown

Bản develop đã có `/health`, `/ready` và lifespan shutdown. Readiness hiện dựa trên cờ khởi tạo, không kiểm tra Redis hoặc database thực tế; không nên coi đó là kiểm tra dependency. Kiểm thử trong container: `/health` và `/ready` trả 200; gửi SIGTERM khoảng 40 ms sau khi bắt đầu request, request trả 200 và process thoát mã 0. Đây là một lần thử với mock LLM, không bảo đảm mọi tình huống shutdown.

## 5.3–5.5 Stateless và load balancing

Đã bỏ fallback session trong memory ở bản production: session luôn lưu trong Redis; `/ready` trả 503 nếu Redis không kết nối được. Việc thêm message dùng Lua để tránh mất cập nhật khi nhiều instance ghi đồng thời. Đã sửa số turn bị cộng dư một.

Chạy Compose với ba agent, Redis và Nginx. Script `test_stateless.py` gửi 5 request; cả ba instance đều xử lý request và history có 10 message. Sau khi dừng một container agent, `GET` history vẫn trả 200 và tiếp tục `/chat` với cùng session trả 200, turn 6, storage Redis. Đã dừng stack sau kiểm thử. Script sẵn có không tự dừng instance; thao tác dừng được thực hiện riêng.

Hạn chế: Nginx resolve upstream lúc khởi động, cần xem xét cập nhật DNS khi container thay địa chỉ; kiểm thử trên không chứng minh failover không gián đoạn cho mọi request. Redis không sẵn sàng làm request session thất bại thay vì chuyển sang bộ nhớ cục bộ.

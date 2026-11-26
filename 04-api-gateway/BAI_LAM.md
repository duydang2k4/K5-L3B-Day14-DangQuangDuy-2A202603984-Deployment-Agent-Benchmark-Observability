# Bài làm Part 4

## 4.1 API key

`verify_api_key` được inject vào `/ask`, đọc `X-API-Key`: thiếu trả 401, sai trả 403. Key lấy từ `AGENT_API_KEY` lúc khởi động; rotate bằng cách cập nhật biến và khởi động lại, đồng thời chuyển client sang key mới. Ví dụ basic có key mặc định và in key khi khởi động, không phù hợp production. Kiểm thử HTTP trong container xác nhận thiếu/sai/đúng key lần lượt trả 401/403/200.

## 4.2 JWT

`POST /auth/token` xác thực tài khoản demo và ký JWT HS256 chứa subject, role và thời hạn 60 phút. `/ask` xác minh chữ ký và hạn token từ Bearer header. Tài liệu lab ghi `/token` và admin/secret nhưng code dùng `/auth/token` và tài khoản demo trong `auth.py`. Secret mặc định và mật khẩu demo không phù hợp production. Kiểm thử student/demo123 lấy token và gọi `/ask` đều trả 200.

## 4.3 Rate limit

Sliding window lưu timestamp trong deque theo user: user 10 request/60 giây, admin 100/60 giây, không bypass hoàn toàn. State trong memory không chia sẻ giữa các process và mất khi restart. Kiểm thử 11 request liên tiếp với token student: 10 lần 200, lần thứ 11 trả 429.

## 4.4 Cost guard

Đã thêm `production/monthly_cost_guard.py`: lưu ngân sách 10 USD theo user và tháng UTC trong Redis; Lua thực hiện kiểm tra và cộng dự toán nguyên tử. Key dùng hash user, TTL 32 ngày được làm mới khi dùng; key tháng mới tự đặt lại ngân sách. Chạy thử Redis tạm: lần lượt dự toán 6, 4 và 0,01 USD trả `True, True, False`. Đây là hàm đặt trước chi phí dự toán độc lập, chưa tích hợp vào `/ask` hoặc đối soát chi phí thực tế.

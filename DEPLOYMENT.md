# Deployment — Render

Public URL: https://k5-l3b-day14-dangquangduy-2a202603984.onrender.com/

Service Python 3.11.11, Root Directory `06-lab-complete`, commit triển khai `c0fba4bb83b1ca661f6815914a4b59c8adf81220`. Lệnh chạy: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Render Key Value được kết nối qua `REDIS_URL`.

Biến môi trường được đặt: `PYTHON_VERSION`, `REDIS_URL`, `AGENT_API_KEY`, `ENVIRONMENT`. `PORT` do Render cấp; `RATE_LIMIT_PER_MINUTE` và `DAILY_BUDGET_USD` dùng giá trị mặc định trong ứng dụng nếu không được đặt. Không lưu giá trị secret trong repo.

## Kiểm tra

```powershell
$url = 'https://k5-l3b-day14-dangquangduy-2a202603984.onrender.com'
Invoke-RestMethod "$url/health"
Invoke-RestMethod "$url/ready"
curl.exe -i -X POST "$url/ask"
$apiKey = Read-Host 'Nhập AGENT_API_KEY (không chia sẻ)'
$body = @{ question = 'Hello' } | ConvertTo-Json
$response = Invoke-WebRequest -UseBasicParsing -Method Post -Uri "$url/ask" -Headers @{ 'X-API-Key' = $apiKey } -ContentType 'application/json' -Body $body
[System.Text.Encoding]::UTF8.GetString($response.RawContentStream.ToArray()) | ConvertFrom-Json
```

Ngày 26/11/2026: `/health` và `/ready` trả 200; POST `/ask` thiếu key trả 401. Người học kiểm thử request có key và nhận câu trả lời mock thành công. Không cần gửi key cho người khác.

## Ảnh minh chứng

- [Render dashboard](screenshots/dashboard.png)
- [Service Live](screenshots/running.png)
- [Kết quả `/health` và `/ready`](screenshots/test.png)
- [Kết quả `/ask` có key hợp lệ](screenshots/ask.png)

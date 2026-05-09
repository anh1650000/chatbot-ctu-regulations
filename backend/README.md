# Backend API - CTU Regulations Chatbot

## Cài đặt

```bash
cd backend
pip install -r requirements.txt
```

## Database Setup

1. Chạy script SQL để tạo database và tables:

```bash
mysql -u root -p < ../sql-file.sql
```

2. Cấu hình `.env` file (đã có sẵn):

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=adminAnh
DB_NAME=ctu_regulations
DB_PASSWORD=162005DuyAnh_
```

## Chạy server

```bash
# Từ thư mục backend
uvicorn app.main:app --reload

# Hoặc từ thư mục root
python -m uvicorn backend.app.main:app --reload
```

Server sẽ chạy tại: http://127.0.0.1:8000

## API Endpoints

### Chat

-   `GET /api/ask?question={text}` - Hỏi đáp với chatbot

### User Authentication

-   `POST /api/user/register` - Đăng ký user mới

    ```json
    {
        "username": "string",
        "password": "string",
        "name": "string"
    }
    ```

-   `POST /api/user/login` - Đăng nhập

    ```json
    {
        "username": "string",
        "password": "string"
    }
    ```

-   `GET /api/user/check_username?username={username}` - Kiểm tra username tồn tại

### Conversation History

-   `POST /api/user/conversation` - Lưu conversation

    ```json
    {
        "user_id": 1,
        "message": "string",
        "reply": "string"
    }
    ```

-   `GET /api/user/conversation/{user_id}?limit=50` - Lấy lịch sử chat
-   `DELETE /api/user/conversation/{user_id}` - Xóa toàn bộ lịch sử

## Testing

Truy cập: http://127.0.0.1:8000/docs để xem API documentation (Swagger UI)

## Notes

-   Password được hash bằng bcrypt
-   CORS đã enable cho frontend
-   Mặc định lấy 50 conversations gần nhất

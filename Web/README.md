# Frontend - CTU Regulations Chatbot

## Tính năng

### 1. Chat không cần đăng nhập (Anonymous Mode)

-   Người dùng có thể chat ngay mà không cần tạo tài khoản
-   Lịch sử chat lưu trong **localStorage** của trình duyệt
-   Hiển thị trạng thái: **"Khách"**
-   Nút **"Xóa lịch sử"** để xóa localStorage

### 2. Chat với tài khoản (Logged-in Mode)

-   Đăng ký/đăng nhập để lưu lịch sử vào **database**
-   Lịch sử chat được đồng bộ trên nhiều thiết bị
-   Hiển thị tên user
-   Nút **"Xóa lịch sử"** xóa dữ liệu trên server

## Cấu trúc File

```
Web/
├── index.html          # Trang chat chính
├── login.html          # Trang đăng nhập
├── register.html       # Trang đăng ký
├── css/
│   ├── style.css
│   ├── auth.css
│   └── chat.css
└── js/
    ├── config.js       # API configuration
    ├── main.js         # Main app logic
    ├── auth.js         # Authentication
    ├── chat.js         # Chat functionality
    └── utils.js        # Utility functions
```

## API Configuration

File `js/config.js` chứa tất cả endpoints:

```javascript
const API_CONFIG = {
    baseUrl: "http://127.0.0.1:8000",
    endpoints: {
        ask: "/api/ask",
        userRegister: "/api/user/register",
        userLogin: "/api/user/login",
        // ... etc
    },
};
```

## Cách sử dụng

### Chạy Frontend

**Option 1: Mở trực tiếp file HTML**

```bash
# Mở Web/index.html bằng trình duyệt
start Web/index.html
```

**Option 2: Sử dụng Live Server (recommended)**

-   Cài extension "Live Server" trong VS Code
-   Right-click `index.html` → "Open with Live Server"
-   Truy cập: http://localhost:5500/Web/

### Sử dụng Anonymous Mode

1. Mở trang chủ (không cần đăng nhập)
2. Nhập câu hỏi và chat
3. Lịch sử lưu trong localStorage
4. Click "Xóa lịch sử" nếu muốn xóa

### Sử dụng với tài khoản

1. **Đăng ký**: Click "Đăng ký" → Nhập thông tin

    - Username: tối thiểu 5 ký tự
    - Password: tối thiểu 6 ký tự, có chữ hoa, chữ thường, số, ký tự đặc biệt
    - Name: tên hiển thị

2. **Đăng nhập**: Click "Đăng nhập" → Nhập username/password

3. **Chat**: Lịch sử tự động lưu vào database

4. **Đăng xuất**: Click "Đăng xuất"

## LocalStorage Data Structure

### Anonymous User

```javascript
// Key: "chat_history_guest"
[
    {
        message: "Câu hỏi",
        reply: "Câu trả lời",
        created_at: "2025-11-02T10:30:00.000Z",
    },
];
```

### Logged-in User (fallback)

```javascript
// Key: "chat_history_{user_id}"
// Tương tự như guest
```

## Giới hạn

-   **localStorage**: Lưu tối đa 200 conversations
-   **Database**: Mặc định lấy 50 conversations gần nhất

## Troubleshooting

### Lỗi CORS

Đảm bảo backend đã enable CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Không load được lịch sử

-   Kiểm tra backend đang chạy: http://127.0.0.1:8000
-   Kiểm tra Console trong DevTools (F12)
-   Verify user_id trong localStorage

### Clear cache

```javascript
// Mở Console (F12) và chạy:
localStorage.clear();
location.reload();
```

## Development Notes

### Thêm endpoint mới

1. Thêm vào `config.js`:

    ```javascript
    endpoints: {
        newEndpoint: "/api/new";
    }
    ```

2. Sử dụng:
    ```javascript
    fetch(API_CONFIG.getUrl(API_CONFIG.endpoints.newEndpoint));
    ```

### Thay đổi base URL

Chỉ cần sửa 1 dòng trong `config.js`:

```javascript
baseUrl: "https://your-production-api.com";
```

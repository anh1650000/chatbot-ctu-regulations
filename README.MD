# 🤖 Chatbot CTU Regulations

Chatbot giúp sinh viên Đại học Cần Thơ (CTU) tra cứu nhanh các quy định/quy chế học vụ thông qua giao diện web và API backend. Hệ thống sử dụng tìm kiếm kết hợp BM25 + FAISS (Hybrid Search) và tích hợp LLM cục bộ qua Ollama để tạo câu trả lời ngắn gọn, đúng ngữ cảnh.

---

## 🚀 Tính năng chính (hiện có)

- 🔍 Hybrid Search: Kết hợp BM25 (từ khóa) + FAISS (ngữ nghĩa) với trọng số hợp nhất.
- 🇻🇳 Xử lý tiếng Việt: Chuẩn hóa văn bản, tách từ, loại stopwords, đồng nghĩa; hỗ trợ bỏ dấu cho truy vấn mơ hồ.
- 🧠 LLM local (Ollama) qua LangChain: Sinh câu trả lời tự nhiên theo ngữ cảnh truy xuất được.
- ⚡ Streaming từ backend: Trả lời theo thời gian thực.

Lưu ý: Các tính năng như phân loại intent, lưu lịch sử hội thoại lâu dài, và web search fallback hiện chưa kích hoạt trong mã nguồn mặc định.

---

## 🏗️ Kiến trúc hệ thống

Trình duyệt (HTML + CSS3)
→ FastAPI Backend (Python)
→ Pipeline tìm kiếm (BM25 + FAISS: accent + non-accent)
→ MySQL (lưu cấu trúc văn bản nhiều cấp) và tệp dữ liệu nguồn (data/)
→ LLM (Ollama) qua LangChain để sinh câu trả lời

### ✨ Ưu điểm kiến trúc

**1. Hybrid Search (BM25 + FAISS)**

- ✅ Kết hợp điểm mạnh của cả 2 phương pháp: BM25 bắt từ khóa chính xác, FAISS hiểu ngữ nghĩa
- ✅ Dual FAISS index (có dấu + không dấu): Xử lý linh hoạt khi người dùng gõ thiếu dấu hoặc gõ sai chính tả
- ✅ Trọng số động: Có thể điều chỉnh α (BM25) và β (FAISS) để tối ưu theo từng loại câu hỏi

**2. Cấu trúc dữ liệu phân cấp (MySQL)**

- ✅ Tổ chức 4 cấp (document → chapter → article → clause): Dễ quản lý, mở rộng dữ liệu
- ✅ GROUP_CONCAT context: Lấy ngữ cảnh đầy đủ từ nhiều cấp độ trong 1 truy vấn, giảm latency
- ✅ Hỗ trợ truy vết nguồn: Biết chính xác thông tin từ văn bản/điều khoản nào

**3. RAG với LLM Local (Ollama)**

- ✅ Riêng tư & bảo mật: Không gửi dữ liệu ra bên ngoài, phù hợp với quy định nội bộ
- ✅ Không giới hạn API calls: Chi phí vận hành thấp, không phụ thuộc bên thứ 3
- ✅ Streaming response: UX mượt mà, người dùng thấy câu trả lời ngay lập tức

**4. Tiền xử lý tiếng Việt chuyên biệt**

- ✅ Stopwords + synonyms: Cải thiện độ chính xác tìm kiếm
- ✅ Chuẩn hóa Unicode: Xử lý đúng các ký tự đặc biệt tiếng Việt
- ✅ Query preprocessing: Mở rộng câu hỏi với từ đồng nghĩa tự động

**5. Kiến trúc module hóa**

- ✅ Tách biệt services: Dễ bảo trì, test và nâng cấp từng thành phần độc lập
- ✅ FastAPI async: Xử lý đồng thời nhiều request, hiệu năng cao
- ✅ Hot-reload: Phát triển nhanh với `--reload` mode

### Các điểm kỹ thuật chính:

- Dual FAISS index: có cả bản giữ dấu và bản không dấu để tăng độ bền khi người dùng gõ thiếu dấu.
- MySQL dùng để tổ chức dữ liệu theo nhiều cấp (document → chapter → article → clause) và kết hợp với GROUP_CONCAT để lấy ngữ cảnh.
- Prompt được ghép từ kết quả tìm kiếm và truyền cho LLM để sinh đầu ra; phản hồi được stream về frontend.

---

## ⚙️ Công nghệ sử dụng

| Thành phần | Công nghệ                               |
| ---------- | --------------------------------------- |
| Backend    | Python 3.x, FastAPI, LangChain          |
| Tìm kiếm   | FAISS, rank-bm25, tiền xử lý tiếng Việt |
| LLM local  | Ollama (ví dụ: llama3.1:8b)             |
| CSDL       | MySQL 8.x (utf8mb4)                     |
| Frontend   | HTML + CSS3                             |

---

## 🧩 Cấu trúc thư mục chính

```
.
├─ backend/
│  ├─ requirements.txt         # Phụ thuộc Python cho backend
│  └─ app/
│     ├─ main.py              # Khởi tạo FastAPI và router
│     ├─ db.py                # Kết nối CSDL MySQL
│     ├─ routers/
│     │  ├─ ask.py            # API /api/ask – stream câu trả lời từ LLM
│     │  └─ users.py          # API quản lý người dùng
│     ├─ services/
│     │  ├─ bm25_index.py      # Chỉ mục BM25 cho tìm kiếm từ khóa
│     │  ├─ embeddings.py      # Xử lý embeddings cho FAISS
│     │  ├─ faiss_index.py     # Load dual FAISS index (giữ dấu / không dấu)
│     │  ├─ faiss_builder.py   # Xây dựng FAISS index
│     │  ├─ hybrid.py          # Hợp nhất điểm BM25 + FAISS
│     │  ├─ query_preprocessing.py  # Tiền xử lý query tiếng Việt
│     │  ├─ search_services.py # Truy vấn FAISS + lấy kết quả MySQL
│     │  ├─ conversation_service.py  # Quản lý lịch sử hội thoại
│     │  ├─ user_service.py    # Quản lý người dùng
│     │  └─ utils.py           # Hàm tiện ích chung
│     └─ scripts/
│        ├─ build_ollama.py    # Khởi tạo model Ollama qua LangChain
│        └─ embedding_tsne_visualization.py  # Visualize embeddings
│
├─ Web/                       # Frontend HTML tĩnh
│  ├─ index.html              # Trang chủ
│  ├─ login.html              # Trang đăng nhập
│  ├─ register.html           # Trang đăng ký
│  ├─ README.md               # Hướng dẫn frontend
│  ├─ css/
│  │  ├─ style.css            # Style chung
│  │  ├─ auth.css             # Style xác thực
│  │  └─ chat.css             # Style chat
│  └─ js/
│     ├─ main.js              # Script chính
│     ├─ auth.js              # Xử lý xác thực
│     ├─ chat.js              # Xử lý chat
│     ├─ config.js            # Cấu hình API
│     └─ utils.js             # Hàm tiện ích
│
├─ data/                      # Dữ liệu và index
│  ├─ id_mapping.json         # Map vector id → bản ghi
│  ├─ index.faiss             # FAISS index (giữ dấu)
│  ├─ index_none_accent.faiss # FAISS index (không dấu)
│  ├─ synonyms.json           # Từ đồng nghĩa tiếng Việt
│  ├─ vie_stopwords.txt       # Stopwords tiếng Việt
│  └─ qa_history.json         # Lịch sử Q&A
│
├─ raw_data/                  # Dữ liệu thô từ các quy định
│  ├─ level_*.txt             # Các file quy định/quy chế chi tiết
│  └─ full_context_*.txt      # Các file ngữ cảnh đầy đủ
│
├─ docs/                      # Tài liệu thiết kế cơ sở dữ liệu
│  ├─ chatbot_cdm.cdm
│  ├─ chatbot_cdm.cdb
│  ├─ Conceptual Data_1.pdm
│  ├─ PhysicalDataModel_2.cdm
│  ├─ PhysicalDataModel_2.cdb
│  ├─ PhysicalDataModel_2.pdm
│  └─ BAO_CAO_NIEN_LUAN_CO_SO.docx
│
├─ chuanhoa.py               # Script tiền xử lý/ingest dữ liệu vào DB
├─ normalize_raw_data.py     # Chuẩn hóa dữ liệu thô
├─ sql-file.sql              # Lược đồ CSDL MySQL
├─ requirements.txt          # Phụ thuộc chung (thêm theo nhu cầu)
└─ README.MD                 # Tài liệu này
```

---

## 🔧 Chuẩn bị môi trường

1. Sao chép biến môi trường mẫu và chỉnh sửa thông số kết nối:

```powershell
Copy-Item backend/.env.example backend/.env
```

2. Cài đặt Python packages (khuyến nghị dùng venv):

```powershell
# Tạo và kích hoạt môi trường ảo (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Cài đặt phụ thuộc (cập nhật requirements.txt theo nhu cầu)
pip install -r requirements.txt
```

3. Khởi động Ollama và kéo model (ví dụ llama3.1:8b):

```powershell
ollama pull llama3.1:8b
ollama run llama3.1:8b
```

4. Xây FAISS index (nếu chưa có `data/index.faiss`, `data/index_none_accent.faiss`):

```powershell
python -m backend.app.scripts.build_ollama
```

---

## ▶️ Chạy dự án

Mở 2 terminal:

1. Backend (FastAPI):

```powershell
python -m uvicorn backend.app.main:app --reload
```

Truy cập ứng dụng tại: http://127.0.0.1:8000


---

## 🧭 Ghi chú & hướng phát triển

- Tối ưu prompt và kiểm soát chiều dài ngữ cảnh để tiết kiệm token/latency.
- Bổ sung lưu lịch sử hội thoại (gợi ý: Redis + LangChain Memory hoặc MySQL).
- (Tuỳ chọn) Thêm Intent Detection, UI nâng cao, hoặc Web Search fallback khi nội bộ thiếu dữ liệu.
- Hoàn thiện `requirements.txt` với phiên bản thư viện cụ thể để tái lập môi trường dễ hơn.

---

## 📜 Tác giả

- Phạm Duy Anh – Khoa Khoa học Máy tính, Đại học Cần Thơ (CTU)
- Niên luận Cơ sở ngành Khoa học Máy tính – Học kỳ 1, Năm học 2025–2026

Giấy phép: sử dụng cho mục đích học thuật, tự do chỉnh sửa và mở rộng.

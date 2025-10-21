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

Trình duyệt (Vue 3 + Vite)
	→ FastAPI Backend (Python)
		→ Pipeline tìm kiếm (BM25 + FAISS: accent + non-accent)
		→ MySQL (lưu cấu trúc văn bản nhiều cấp) và tệp dữ liệu nguồn (data/)
		→ LLM (Ollama) qua LangChain để sinh câu trả lời

Các điểm chính:
- Dual FAISS index: có cả bản giữ dấu và bản không dấu để tăng độ bền khi người dùng gõ thiếu dấu.
- MySQL dùng để tổ chức dữ liệu theo nhiều cấp (document → chapter → article → clause) và kết hợp với GROUP_CONCAT để lấy ngữ cảnh.
- Prompt được ghép từ kết quả tìm kiếm và truyền cho LLM để sinh đầu ra; phản hồi được stream về frontend.

---

## ⚙️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|-----------|-----------|
| Backend | Python 3.x, FastAPI, LangChain |
| Tìm kiếm | FAISS, rank-bm25, tiền xử lý tiếng Việt |
| LLM local | Ollama (ví dụ: llama3.1:8b) |
| CSDL | MySQL 8.x (utf8mb4) |
| Frontend | Vue 3 + Vite (cơ bản) |

---

## 🧩 Cấu trúc thư mục chính

```
.
├─ backend/
│  ├─ .env.example              # Mẫu biến môi trường (sao chép thành .env khi chạy)
│  └─ app/
│     ├─ main.py               # Khởi tạo FastAPI và router
│     ├─ db.py                 # Kết nối CSDL
│     ├─ routers/
│     │  ├─ ask.py             # API /api/ask – stream câu trả lời từ LLM
│     │  └─ searchs.py         # API /api/search – hybrid search
│     ├─ services/
│     │  ├─ bm25_index.py
│     │  ├─ embeddings.py
│     │  ├─ faiss_index.py     # Load dual FAISS index (giữ dấu / không dấu)
│     │  ├─ hybrid.py          # Hợp nhất điểm BM25 + FAISS
│     │  ├─ query_preprocessing.py
│     │  ├─ search_services.py # Truy vấn FAISS + lấy kết quả MySQL (GROUP_CONCAT)
│     │  └─ utils.py
│     └─ scripts/
│        ├─ build_index.py     # Xây FAISS index từ dữ liệu
│        └─ build_ollama.py    # Khởi tạo model Ollama qua LangChain
│
├─ frontend/
│  ├─ package.json
│  ├─ vite.config.js
│  └─ src/
│     ├─ main.js, main.vue     # App Vue cơ bản (Vite)
│     ├─ auth.vue, chat.vue    # Một số trang/mẫu
│     ├─ demo_UI.py            # Giao diện Gradio demo (tùy chọn)
│     └─ debug_gradio.py       # Script debug (tùy chọn)
│
├─ data/
│  ├─ README.md                # Hướng dẫn dữ liệu và build index
│  ├─ id_mapping.json          # Map vector id → bản ghi
│  ├─ synonyms.json            # Từ đồng nghĩa
│  ├─ vie_stopwords.txt        # Stopwords tiếng Việt
│  ├─ quy_dinh_cong_tac_hoc_vu_sv_2021_update_k50.txt
│  └─ bieumausv.txt
│  # (Các file lớn sinh ra như *.faiss được ignore)
│
├─ chuanhoa.py                 # Tiền xử lý/ingest dữ liệu vào DB
├─ sql-file.sql                # Lược đồ/tinh chỉnh CSDL
├─ requirements.txt            # (đang để trống – cập nhật tùy môi trường)
└─ .gitignore                  # Đã cấu hình bỏ qua file lớn và môi trường
```

---

## 🔧 Chuẩn bị môi trường

1) Sao chép biến môi trường mẫu và chỉnh sửa thông số kết nối:

```powershell
backend/.env.example backend/.env
```

2) Cài đặt Python packages (khuyến nghị dùng venv):

```powershell
# Tạo và kích hoạt môi trường ảo (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Cài đặt phụ thuộc (cập nhật requirements.txt theo nhu cầu)
pip install -r requirements.txt
```

3) Khởi động Ollama và kéo model (ví dụ llama3.1:8b):

```powershell
ollama pull llama3.1:8b
ollama run llama3.1:8b
```

4) Xây FAISS index (nếu chưa có `data/index.faiss`, `data/index_none_accent.faiss`):

```powershell
python -m backend.app.scripts.build_index
```

---

## ▶️ Chạy dự án

Mở 2 terminal:

1) Backend (FastAPI):

```powershell
python -m uvicorn backend.app.main:app --host localhost --port 8000 --reload
```

2) Frontend (Vite + Vue):

```powershell
cd frontend
npm install
npm run dev
```

Truy cập ứng dụng tại: http://localhost:5173

Endpoint API nội bộ: http://localhost:8000/api/ask và http://localhost:8000/api/search

---

## 🧭 Ghi chú & hướng phát triển

- Tối ưu prompt và kiểm soát chiều dài ngữ cảnh để tiết kiệm token/latency.
- (Tuỳ chọn) Thêm Intent Detection, UI nâng cao, hoặc Web Search fallback khi nội bộ thiếu dữ liệu.
- Tối ưu tiền xử lý dữ liệu,  Phân loại ý tưởng người dùng nâng cao
---

## 📜 Tác giả

- Phạm Duy Anh – Sinh viên Khoa học Máy tính K49, Đại học Cần Thơ
- Niên luận Cơ sở ngành Khoa học Máy tính – Học kỳ 1, Năm học 2025–2026

Giấy phép: sử dụng cho mục đích học thuật, tự do chỉnh sửa và mở rộng.

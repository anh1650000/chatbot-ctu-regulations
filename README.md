# 🤖 Chatbot CTU Regulations

**Chatbot CTU Regulations** là dự án chatbot thông minh giúp sinh viên **Đại học Cần Thơ (CTU)** tra cứu nhanh các **quy định, quy chế học vụ, ký túc xá, học phí, và các chính sách đào tạo** thông qua giao diện web thân thiện.  
Dự án được phát triển trong khuôn khổ **Niên luận ngành Khoa học Máy tính**, với mục tiêu xây dựng một hệ thống **Tìm kiếm kết hợp (Hybrid Search)** giữa **BM25** và **FAISS semantic search**, tích hợp mô hình ngôn ngữ cục bộ **Langchain-LLMs (Ollama)** để sinh câu trả lời tự nhiên, chính xác theo ngữ cảnh.

---

## 🚀 Tính năng chính
- 🔍 **Hybrid Search (BM25 + FAISS)** – Kết hợp tìm kiếm từ khóa và tìm kiếm ngữ nghĩa để tăng độ chính xác.
- 🧠 **Hiểu ngữ cảnh & sinh câu trả lời tự nhiên** – Sử dụng Langchain-ollama LLM local model.
- 🗂️ **Tìm kiếm đa cấp** (document → chapter → article → clause).
- 🏷️ **Phân loại intent & lọc metadata** – Phát hiện chủ đề (học tập, ký túc xá, học phí, v.v.).
- 💬 **Lưu lịch sử hội thoại** – Theo user (MySQL) hoặc tạm local JSON nếu là khách.
- 🌐 **Fallback Web Search** – Khi dữ liệu nội bộ thiếu.
- 🧩 **Giao diện Web Chat (Vue 3 + Tailwind)** – Responsive, trực quan, hiển thị lịch sử chat.

---

## 🏗️ Kiến trúc hệ thống
Frontend (Vue 3 + Tailwind)
↓
FastAPI Backend (Python)
├── Hybrid Search (BM25 + FAISS)
├── Ollama3.1:8b Local Model
├── Database (MySQL)
└── Fallback Web Search


---

## ⚙️ Công nghệ sử dụng
| Thành phần | Công nghệ |
|-------------|------------|
| **Backend** | Python 3.11+, FastAPI, FAISS, Rank-BM25 |
| **Frontend** | Vue 3, TailwindCSS |
| **Database** | MySQL (hoặc SQLite local mode) |
| **Embedding** | Sentence-Transformers (Hugging Face) |
| **LLM local** | GPT4All |
| **Search pipeline** | Hybrid Search + Intent Detection (rule-based) |

---

## 🧩 Cấu trúc thư mục chính


/backend
├── main.py
├── routes/
│ ├── searchs.py
│ └── ask.py
├── services/
│ ├── hybrid.py
│ ├── search_services.py
│ ├── utils.py
│ ├── chat_history.py
│ └── local_history.py
└── scripts/
└── build_index.py
/frontend
├── src/
│ ├── components/
│ └── pages/
└── public/


---

## 💡 Cách chạy dự án
### 1️⃣ Backend (FastAPI)
bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

powershell
ollama run llama3.1:8b

2️⃣ Frontend (Vue 3)
cd frontend
npm install
npm run dev


Truy cập http://localhost:5173

🧠 Hướng phát triển


 NLP sâu (Phân loại/phân lớp ý tưởng người dùng)

 Tích hợp Ollama + Whisper + Piper voice

 Triển khai online (Vercel + Railway)

📚 Tác giả

Phạm Duy Anh – Sinh viên Khoa học Máy tính K49, Đại học Cần Thơ
📅 Niên luận Cơ sở ngành Khoa học Máy tính – Học kỳ 1, Năm học 2025-2026

📜 Giấy phép
&copy ĐHCT 2025 – Tự do sử dụng, chỉnh sửa và phát triển mở rộng.

from fastapi import APIRouter
from ..services.hybrid import hybrid_search
from ..scripts.build_ollama import get_model
from fastapi.responses import StreamingResponse
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional
from ..services.conversation_service import get_conversation_history_text

router = APIRouter()

# ==============================
# SYSTEM PROMPT — bản chuẩn hành vi hội thoại
# ==============================
_system_prompt = """
Bạn là CTU Assistant — trợ lý AI của Đại học Cần Thơ (CTU).
    
Mục tiêu:
- Giải đáp chính xác, ngắn gọn, dựa trên quy định, chính sách, hoặc nội quy của CTU.
- Duy trì mạch hội thoại hợp lý giữa các câu hỏi liên tiếp.
- Thân thiện, lịch sự và nhiệt tình hỗ trợ người dùng.

Nguyên tắc:
1. Ưu tiên thông tin từ "Lịch sử hội thoại" nếu câu hỏi có liên quan đến các lượt trước.
2. Ưu tiên dữ liệu từ phần "Tài liệu tham khảo" để trích dẫn hoặc xác nhận.
3. Nếu hai nguồn mâu thuẫn, tin "Tài liệu tham khảo" hơn.
4. Nếu không có thông tin trong tài liệu, hãy nói rõ: "Tôi không tìm thấy thông tin liên quan trong quy định của CTU."
5. Trả lời rõ ràng, tối đa 3 câu, không lặp lại nội dung câu hỏi.
6. Nếu câu hỏi yêu cầu tính toán (ví dụ: điểm, học bổng...), chỉ suy luận dựa trên thông tin người dùng đã cung cấp trong hội thoại.
7. Nếu câu hỏi không đủ dữ kiện, hãy hỏi lại để làm rõ thay vì trả lời chung chung.

Phong cách trả lời:
- Ngắn gọn, súc tích, đúng trọng tâm.
- Nếu hội thoại đã có ngữ cảnh, chỉ trả lời phần mới hoặc kết luận logic.
"""

# ==============================
# MODEL
# ==============================
_model = get_model()

# ==============================
# ASK API
# ==============================
@router.get("/ask")
def ask(question: str, user_id: Optional[int] = None, conversation_id: Optional[int] = None) -> str:
    question = question.strip()

    if _model is None:
        return "Model is not loaded. Please check the server logs."

    # Kiểm tra câu chào
    greeting_keywords = ["xin chào", "chào", "hello", "hi", "hey"]
    if any(keyword in question.lower() for keyword in greeting_keywords) and len(question.split()) <= 3:
        def greet():
            greeting = """Xin chào! 👋

Tôi là CTU Assistant - trợ lý AI của Đại học Cần Thơ. Tôi được thiết kế để hỗ trợ bạn tra cứu các quy định, chính sách và thông tin về CTU một cách nhanh chóng và chính xác.

Bạn có thể hỏi tôi về:
• 📚 Quy chế đào tạo và học vụ
• 🏠 Quy định ký túc xá
• 💰 Học phí và học bổng
• 📝 Điểm rèn luyện
• 🎓 Chuyển ngành, miễn học phần
• 📋 Các quy định khác của trường

Hãy đặt câu hỏi để tôi có thể giúp bạn nhé! 😊"""
            yield greeting
        return StreamingResponse(greet(), media_type="text/plain")

    template, content, conversation_history = get_template(question, user_id, conversation_id)
    # return content
    prompt = ChatPromptTemplate.from_messages(template)
    chain = prompt | _model

    def generate():
        try:
            for chunk in chain.stream({
                "question": question,
                "content": content,
                "conversation_history": conversation_history,
            }):
                yield chunk if isinstance(chunk, str) else str(chunk)
        except Exception as e:
            yield f"[Error: {e}]"

    return StreamingResponse(generate(), media_type="text/plain")


# ==============================
# TEMPLATE BUILDER
# ==============================
def get_template(question: str, user_id: Optional[int] = None, conversation_id: Optional[int] = None) -> list:
    content = ""
    conversation_history = ""

    # Lấy 10 lượt hội thoại gần nhất (= 20 messages: 10 user + 10 bot)
    if user_id and conversation_id:
        conversation_history = get_conversation_history_text(user_id, conversation_id, limit=20)

    # Tìm tài liệu liên quan
    results = hybrid_search(question)
    for result in results.get("result", []):
        content += result + "\n\n"

    # Tạo prompt
    if conversation_history:
        template = [
            ("system", _system_prompt),
            ("user",
             "Lịch sử hội thoại gần đây:\n{conversation_history}\n\n"
             "Tài liệu tham khảo (chỉ chọn phần liên quan, có thể chứa thông tin dư):\n{content}\n\n"
             "Câu hỏi mới: {question}\n\n"
             "→ Hãy trả lời ngắn gọn (1-3 câu), logic theo ngữ cảnh hội thoại, chỉ dựa vào thông tin có thật.")
        ]
    else:
        template = [
            ("system", _system_prompt),
            ("user",
             "Tài liệu tham khảo (chỉ chọn phần liên quan, có thể chứa thông tin dư):\n{content}\n\n"
             "Câu hỏi: {question}\n\n"
             "→ Hãy trả lời ngắn gọn (1-3 câu), chỉ dựa vào thông tin có thật trong tài liệu.")
        ]

    return template, content, conversation_history

import re
from backend.app.db import get_db_connection
from docx import Document

# =========================
# 1. Kết nối MySQL
# =========================
conn = get_db_connection()  
cursor = conn.cursor()

# =========================
# 2. Hàm insert DB
# =========================
def insert_document(title, source_file):
    cursor.execute(
        "INSERT INTO documents (title, source_file) VALUES (%s, %s)",
        (title, source_file)
    )
    conn.commit()
    return cursor.lastrowid

def insert_chapter(doc_id, number, title):
    cursor.execute(
        "INSERT INTO chapters (doc_id, chapter_number, title) VALUES (%s, %s, %s)",
        (doc_id, number, title)
    )
    conn.commit()
    return cursor.lastrowid

def insert_article(chapter_id, number, title):
    cursor.execute(
        "INSERT INTO articles (chapter_id, article_number, title) VALUES (%s, %s, %s)",
        (chapter_id, number, title)
    )
    conn.commit()
    return cursor.lastrowid

def insert_clause(article_id, number, content):
    cursor.execute(
        "INSERT INTO clauses (article_id, clause_number, content) VALUES (%s, %s, %s)",
        (article_id, number, content)
    )
    conn.commit()

# =========================
# 3. Đọc file DOCX
# =========================

path = r"D:\CTU\CT201E - Niên luận cơ sở ngành KHMT\chatbot-ctu-regulations\data\demo.txt"
with open(path, "r", encoding="utf-8") as f:
    raw_text = f.read()
# =========================
# 4. Regex parse
# =========================
doc_id = insert_document("Quy định công tác học vụ 2021", path)


# def chuan_hoa_van_ban(text: str) -> str:
#     # Thêm \n trước "Điều X."
#     text = re.sub(r"(Điều\s+\d+\.)", r"\n\1", text)

#     # Thêm \n trước số thứ tự (1. , 2. , 10. ...)
#     text = re.sub(r"(\s)(\d+\.\s)", r"\1\n\2", text)

#     # Thêm \n trước chữ cái đánh số (a), b), c)...)
#     text = re.sub(r"(\s)([a-zA-Z]\)\s)", r"\1\n\2", text)

#     # Xoá \n dư thừa (nếu có nhiều dòng trống liên tiếp)
#     text = re.sub(r"\n+", "\n", text)
#     return text.strip()

# raw_text = chuan_hoa_van_ban(raw_text)
# with open(path, "w+", encoding="utf-8") as f:
#     f.write(raw_text)

# # Tách theo chương
chapter_blocks = re.split(r"(^Chương\s+[IVXLC]+.*)", raw_text, flags=re.MULTILINE)

for i in range(1, len(chapter_blocks), 2):
    chapter_title = chapter_blocks[i].strip()
    chapter_number = re.findall(r"^Chương\s+([IVXLC]+)", chapter_title, flags=re.MULTILINE)[0]
    # print(f"{chapter_title}\n")
    chapter_id = insert_chapter(doc_id, i//2+1, chapter_title)

    chapter_content = chapter_blocks[i+1]
    # print(f"{chapter_content}\n")
#     # Tách theo Điều
    article_blocks = re.split(r"(^Điều\s+\d+\.?.*)", chapter_content, flags=re.MULTILINE)

    for j in range(1, len(article_blocks), 2):
        article_title = article_blocks[j].strip()
        article_number = re.findall(r"^Điều\s+(\d+)", article_title, flags=re.MULTILINE)[0]
        # print(f"{article_title}\n")
        article_id = insert_article(chapter_id, int(article_number), article_title)

        article_content = article_blocks[j+1].strip()
        # print(f"{article_content}\n")
#         # Tách theo Khoản (1., 2., ...)
        clause_blocks = re.split(r"(^\d+\.\s)", article_content, flags=re.MULTILINE)

        if len(clause_blocks) > 1:
            # Có nhiều khoản
            for k in range(1, len(clause_blocks), 2):
                clause_number = int(clause_blocks[k].replace(".", "").strip())
                clause_content = clause_blocks[k+1].strip()
                # print(f"index {k}: {article_number}.{clause_number} {clause_content}\n")
                insert_clause(article_id, clause_number, clause_content)
        else:
            # print("index: -1 " + article_content + "\n")
#             # Không có khoản → lưu nguyên điều
            insert_clause(article_id, None, article_content)

# print("✅ Import DOCX vào DB xong")

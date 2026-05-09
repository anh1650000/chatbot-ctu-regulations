import re
from backend.app.db import get_db_connection
from docx import Document
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ***FILE NÀY EM VIẾT, Ý TƯỞNG CỦA EM VÀ EM CÓ NHỜ AI DEBUG******
# =========================
# 1. Kết nối MySQL
# =========================
conn = get_db_connection()  
cursor = conn.cursor()

# =========================
# 2. Cấu hình chunking - EXACT COPY TỪ ANALYZE_CHUNKS_DISTRIBUTION.PY
# =========================
CHUNK_SIZE = 750
CHUNK_OVERLAP = 120

def count_tokens_simple(text: str) -> int:
    """Ước lượng số token cho tiếng Việt - khớp với logic chuẩn"""
    words = text.split()
    return int(len(words) * 1.3)

def token_length_function(text: str) -> int:
    """Hàm tính token count thực tế cho text_splitter"""
    return count_tokens_simple(text)

# Separators ưu tiên cấu trúc văn bản pháp lý Việt Nam:
# Tách theo: Điều → Nhóm → Khoản [1., 2., ...] → Sub-items → Paragraph → Newline
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=token_length_function,  # ✅ Dùng token count, không phải character count
    separators=[
        "\nĐiều ",
        "\nNhóm ",
        "\n1. ", "\n2. ", "\n3. ", "\n4. ", "\n5. ", "\n6. ", "\n7. ", "\n8. ", "\n9. ", "\n10. ",
        "\na) ", "\nb) ", "\nc) ", "\nd) ", "\ne) ", "\nf) ", 
        "\n\n",
        "\n"
    ]
)

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
# 3. Hàm chia chunk - EXACT COPY TỪ ANALYZE_CHUNKS_DISTRIBUTION.PY
# =========================
def split_text_to_chunks(text: str) -> list:
    """Chia text thành chunks nếu > 800 tokens, ngược lại giữ nguyên - EXACT SAME từ analyze"""
    estimated_tokens = count_tokens_simple(text)
    
    if estimated_tokens <= 800:  # ✅ Threshold = 800 (khớp với analyze)
        return [text]
    else:
        return text_splitter.split_text(text)

def process_chapter_content(chapter_id: int, chapter_content: str, doc_title: str = None):
    """Xử lý nội dung chương: tách theo Điều → Mục → chunks"""
    
    article_blocks = re.split(r"(^Điều\s+\d+\.?.*)", chapter_content, flags=re.MULTILINE)
    
    if len(article_blocks) == 1:
        # Không có Điều - check for Mục
        section_blocks = re.split(r"(^Mục\s+\d+\.?.*)", chapter_content, flags=re.MULTILINE)
        
        if len(section_blocks) == 1:
            # Không có Mục nữa - treat as single article
            chunks = split_text_to_chunks(chapter_content.strip())
            article_id = insert_article(chapter_id, 1, doc_title or "Nội dung")
            print(f"      ✅ INSERT Article 1: article_id={article_id} (single)")
            
            for idx, chunk in enumerate(chunks, 1):
                insert_clause(article_id, idx, chunk)
            
            tokens = sum(count_tokens_simple(c) for c in chunks)
            print(f"      ✅ INSERT {len(chunks)} Clauses: {tokens} tokens total")
        else:
            # Có Mục - xử lý như trong process_section_as_article
            for j in range(1, len(section_blocks), 2):
                section_title = section_blocks[j].strip()
                section_content = section_blocks[j+1].strip() if j+1 < len(section_blocks) else ""
                
                sec_num_match = re.search(r'Mục\s+(\d+)', section_title)
                section_number = int(sec_num_match.group(1)) if sec_num_match else 1
                
                if not section_content:
                    print(f"      ⏭️  Skip {section_title}: No content")
                    continue
                
                chunks = split_text_to_chunks(section_content)
                article_id = insert_article(chapter_id, section_number, section_title)
                print(f"      ✅ INSERT Article (Mục): article_id={article_id} | {section_title}")
                
                for idx, chunk in enumerate(chunks, 1):
                    insert_clause(article_id, idx, chunk)
                
                tokens = sum(count_tokens_simple(c) for c in chunks)
                print(f"         ✅ INSERT {len(chunks)} Clauses: {tokens} tokens")
    else:
        # Có Điều
        for j in range(1, len(article_blocks), 2):
            article_title = article_blocks[j].strip()
            article_content = article_blocks[j+1].strip() if j+1 < len(article_blocks) else ""
            
            # Extract article number
            arti_num_match = re.search(r'Điều\s+(\d+)', article_title)
            article_number = int(arti_num_match.group(1)) if arti_num_match else 1
            
            if not article_content:
                # Lưu article title khi ko có nội dung
                article_id = insert_article(chapter_id, article_number, article_title)
                insert_clause(article_id, 1, article_title)
                print(f"      ✅ INSERT Article (title only): article_id={article_id} | {article_title}")
                continue
            
            # Chia chunks
            chunks = split_text_to_chunks(article_content)
            article_id = insert_article(chapter_id, article_number, article_title)
            print(f"      ✅ INSERT Article: article_id={article_id} | {article_title}")
            
            for idx, chunk in enumerate(chunks, 1):
                insert_clause(article_id, idx, chunk)
            
            tokens = sum(count_tokens_simple(c) for c in chunks)
            print(f"         ✅ INSERT {len(chunks)} Clauses: {tokens} tokens")



def process_section_as_article(chapter_id: int, content: str):
    """Xử lý Mục như Điều - chia chunks nếu cần"""
    
    section_blocks = re.split(r"(^Mục\s+\d+\.?.*)", content, flags=re.MULTILINE)
    
    if len(section_blocks) == 1:
        # Không có Mục - treat as single article
        chunks = split_text_to_chunks(content.strip())
        article_id = insert_article(chapter_id, 1, "Nội dung")
        print(f"      ✅ INSERT Article 1: article_id={article_id} (no sections)")
        
        for idx, chunk in enumerate(chunks, 1):
            insert_clause(article_id, idx, chunk)
        
        tokens = sum(count_tokens_simple(c) for c in chunks)
        print(f"      ✅ INSERT {len(chunks)} Clauses: {tokens} tokens total")
    else:
        # Có Mục
        for j in range(1, len(section_blocks), 2):
            section_title = section_blocks[j].strip()
            section_content = section_blocks[j+1].strip() if j+1 < len(section_blocks) else ""
            
            # Extract section number
            sec_num_match = re.search(r'Mục\s+(\d+)', section_title)
            section_number = int(sec_num_match.group(1)) if sec_num_match else 1
            
            if not section_content:
                print(f"      ⏭️  Skip {section_title}: No content")
                continue
            
            # Chia chunks
            chunks = split_text_to_chunks(section_content)
            article_id = insert_article(chapter_id, section_number, section_title)
            print(f"      ✅ INSERT Article (Mục): article_id={article_id} | {section_title}")
            
            for idx, chunk in enumerate(chunks, 1):
                insert_clause(article_id, idx, chunk)
            
            tokens = sum(count_tokens_simple(c) for c in chunks)
            print(f"         ✅ INSERT {len(chunks)} Clauses: {tokens} tokens")

# =========================
# 4. Đọc và xử lý files
# =========================

raw_data_dir = Path(__file__).parent / "raw_data"
level_files = sorted(raw_data_dir.glob("level*.txt"))
full_context_files = sorted(raw_data_dir.glob("full_context*.txt"))
all_files = level_files + full_context_files

print(f"Tổng số file level: {len(level_files)}")
print(f"Tổng số file full_context: {len(full_context_files)}")
print(f"Tổng số file: {len(all_files)}\n")

processed_files = set()  # Track files đã xử lý

for file_path in all_files:
    if file_path.name in processed_files:
        print(f"⏭️  Bỏ qua (đã xử lý): {file_path.name}\n")
        continue
    
    processed_files.add(file_path.name)
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    lines = raw_text.split('\n')
    doc_title = lines[0].strip() if len(lines) > 0 else "Untitled"
    doc_source = lines[1].strip() if len(lines) > 1 else ""
    content = '\n'.join(lines[2:]).strip()
    
    print(f"{'='*80}")
    print(f"📄 File: {file_path.name}")
    print(f"📌 Tựa đề: {doc_title}")
    print(f"🔗 Source: {doc_source}\n")
    
    # Insert document
    doc_id = insert_document(doc_title, doc_source)
    print(f"   ✅ INSERT Document: doc_id={doc_id}")
    
    is_full_context = file_path.name.startswith("full_context")
    
    if is_full_context:
        # ========== FULL_CONTEXT ==========
        print(f"📦 Loại: FULL_CONTEXT\n")
        
        chapter_id = insert_chapter(doc_id, 1, doc_title)
        print(f"   ✅ INSERT Chapter: chapter_id={chapter_id}")
        article_id = insert_article(chapter_id, 1, doc_title)
        print(f"   ✅ INSERT Article: article_id={article_id}")
        
        chunks = split_text_to_chunks(content)
        for idx, chunk in enumerate(chunks, 1):
            insert_clause(article_id, idx, chunk)
        
        tokens = sum(count_tokens_simple(c) for c in chunks)
        print(f"   ✅ INSERT {len(chunks)} Clauses: {tokens} tokens total\n")
    
    else:
        # ========== LEVEL FILES ==========
        print(f"📦 Loại: LEVEL\n")
        
        # 1. Check for CHƯƠNG structure
        chapter_blocks = re.split(r"(^CHƯƠNG\s+[IVXLC]+.*|^Chương\s+[IVXLC]+.*)", content, flags=re.MULTILINE | re.IGNORECASE)
        
        if len(chapter_blocks) > 1:
            # ✅ HAS CHAPTERS
            print(f"   📋 Cấu trúc: Chương → Điều")
            for i in range(1, len(chapter_blocks), 2):
                chapter_title = chapter_blocks[i].strip()
                chapter_number = i // 2 + 1
                chapter_id = insert_chapter(doc_id, chapter_number, chapter_title)
                print(f"   ✅ INSERT Chapter {chapter_number}: chapter_id={chapter_id} | {chapter_title}")
                
                chapter_content = chapter_blocks[i+1]
                process_chapter_content(chapter_id, chapter_content, doc_title)
        
        else:
            # 2. NO CHAPTERS - Check for PHẦN structure
            part_blocks = re.split(r"(^Phần\s+\d+\.?.*|^PHẦN\s+\d+\.?.*)", content, flags=re.MULTILINE | re.IGNORECASE)
            
            if len(part_blocks) > 1:
                # ✅ HAS PARTS (Phần = Chương, Mục = Điều)
                print(f"   📋 Cấu trúc: Phần → Mục")
                for i in range(1, len(part_blocks), 2):
                    part_title = part_blocks[i].strip()
                    part_number = i // 2 + 1
                    chapter_id = insert_chapter(doc_id, part_number, part_title)
                    print(f"   ✅ INSERT Part {part_number} (as Chapter): chapter_id={chapter_id} | {part_title}")
                    
                    part_content = part_blocks[i+1]
                    # Phần → Mục (Mục = Article)
                    process_section_as_article(chapter_id, part_content)
            
            else:
                # 3. NO CHAPTERS, NO PARTS - use virtual chapter with doc_title
                print(f"   📋 Cấu trúc: Chỉ Điều (hoặc Mục)")
                chapter_id = insert_chapter(doc_id, 1, doc_title)
                print(f"   ✅ INSERT Virtual Chapter: chapter_id={chapter_id}")
                process_chapter_content(chapter_id, content, doc_title)
    
    print(f"✅ Hoàn thành: {file_path.name}\n")

print("="*80)
print("✅ Import tất cả files vào DB xong!")
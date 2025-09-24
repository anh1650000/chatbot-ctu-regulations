from fastapi import APIRouter, Query
from underthesea import word_tokenize
from ..db import get_db_connection

router = APIRouter()

@router.get("/search")
def search(query: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    try:
        
        # 1. Search document
        cursor.execute("SELECT * FROM documents WHERE title LIKE %s", (f"%{query}%",))
        doc = cursor.fetchone()
        if doc:
            cursor.execute("SELECT * FROM chapters WHERE doc_id = %s", (doc["doc_id"],))
            chapters = cursor.fetchall()
            for chap in chapters:
                cursor.execute("SELECT * FROM articles WHERE chapter_id = %s", (chap["chapter_id"],))
                articles = cursor.fetchall()
                for art in articles:
                    cursor.execute("SELECT * FROM clauses WHERE article_id = %s", (art["article_id"],))
                    clauses = cursor.fetchall()
                    art["clauses"] = clauses
                chap["articles"] = articles
            doc["chapters"] = chapters
            return {"level": "document", "result": doc}

        # 2. Search chapter
        cursor.execute("SELECT * FROM chapters WHERE title LIKE %s", (f"%{query}%",))
        chap = cursor.fetchone()
        if chap:
            cursor.execute("SELECT * FROM articles WHERE chapter_id = %s", (chap["chapter_id"],))
            articles = cursor.fetchall()
            for art in articles:
                cursor.execute("SELECT * FROM clauses WHERE article_id = %s", (art["article_id"],))
                clauses = cursor.fetchall()
                art["clauses"] = clauses
            chap["articles"] = articles
            return {"level": "chapter", "result": chap}

        # 3. Search article
        cursor.execute("SELECT * FROM articles WHERE title LIKE %s", (f"%{query}%",))
        art = cursor.fetchone()
        if art:
            cursor.execute("SELECT * FROM clauses WHERE article_id = %s", (art["article_id"],))
            clauses = cursor.fetchall()
            art["clauses"] = clauses
            return {"level": "article", "result": art}

        # 4. Search clause
        cursor.execute("SELECT * FROM clauses WHERE content LIKE %s", (f"%{query}%",))
        clause = cursor.fetchone()
        if clause:
            return {"level": "clause", "result": clause}

        return {"level": "none", "result": []}

    finally:
        cursor.close()
        conn.close()

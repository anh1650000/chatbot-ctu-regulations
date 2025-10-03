from ..db import get_db_connection

def load_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    try:
        cursor.execute("""
            SELECT 
                d.doc_id, 
                d.title as doc_title, 
                d.source_file as doc_source_file, 
                ch.chapter_id, 
                ch.title as chapter_title, 
                a.article_id, 
                a.title as article_title,
                group_concat(cl.content SEPARATOR '\n') as all_clauses_content
            FROM documents d
            JOIN chapters ch on d.doc_id = ch.doc_id
            JOIN articles a on ch.chapter_id = a.chapter_id
            JOIN clauses cl on cl.article_id = a.article_id
            GROUP BY a.article_id
        """)
        data = cursor.fetchall()
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def text_splitter(data):
    text_chunks = []
    meta_data = []
    
    for row in data:
        chunk = f"{row['article_title']}\n{row['all_clauses_content']}"
        chunk = chunk.lower()
        text_chunks.append(chunk)
        meta_data.append({
            'doc_id': row['doc_id'],
            'chapter_id': row['chapter_id'], 
            'article_id': row['article_id'],
        })

    return text_chunks, meta_data

def search_nested_structure(query: str):
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
                    art["all_clause_content"] = clauses
                chap["articles"] = articles
            doc["chapters"] = chapters
            return {"level": "document",
                    "result": doc}
        
        # 2. Search chapter
        cursor.execute("SELECT * FROM chapters WHERE title LIKE %s", (f"%{query}%",))
        chap = cursor.fetchone()
        
        if chap:
            cursor.execute("SELECT * FROM articles WHERE chapter_id = %s", (chap["chapter_id"],))
            articles = cursor.fetchall()
            for art in articles:
                cursor.execute("SELECT * FROM clauses WHERE article_id = %s", (art["article_id"],))
                clauses = cursor.fetchall()
                if clauses:
                    art["all_clause_content"] = clauses
            chap["articles"] = articles
        
            cursor.execute("""SELECT d.title AS document_title 
                           FROM documents d
                            JOIN chapters c ON d.doc_id = c.doc_id 
                            WHERE c.chapter_id = %s""", (chap["chapter_id"],))
            doc_chap = cursor.fetchone()
            
            if doc_chap:
                chap["document_title"] = doc_chap["document_title"]
            
            return {"level": "chapter",
                    "result": chap}
        
        #3. Search article
        cursor.execute("SELECT * FROM articles WHERE title LIKE %s", (query,))
        art = cursor.fetchone()
        if art:
            cursor.execute("""SELECT *
                           FROM clauses
                           WHERE article_id = %s
                           """, (art["article_id"],))
            clauses = cursor.fetchall()
            art["all_clause_content"] = clauses

            cursor.execute("""SELECT d.title AS document_title, c.title AS chapter_title 
                           FROM documents d 
                           JOIN chapters c ON d.doc_id = c.doc_id 
                           JOIN articles a ON c.chapter_id = a.chapter_id 
                           WHERE a.article_id = %s""", (art["article_id"],))
            doc_chap = cursor.fetchone()
            
            if doc_chap:
                art["document_title"] = doc_chap["document_title"]
                art["chapter_title"] = doc_chap["chapter_title"]
                    
            return {"level": "article",
                    "result": art}

        # If no matches found
        return {"level": "none", "result": []}
    
    except Exception as e:
        return {"level": "error", "result": str(e)}
        
    finally:
        cursor.close()
        conn.close()


def normalize_nested_structure(data: dict) -> dict:

    level = data.get("level")
    result = data.get("result", {})
    normalized_result = []
    
    if level == "document":
        normalized = {
            "document_title": result.get("title"),
            "source_file": result.get("source_file"), 
            "chapters": []
        }
        for chap in result.get("chapters", []):
            chapter_info = {
                "chapter_title": chap.get("title"),
                "articles": []
            }
            for art in chap.get("articles", []):
                article_info = {
                    "article_title": art.get("title"),
                    "clause_content": "\n".join([cl.get("content", "") for cl in art.get("all_clause_content", [])])
                }
                chapter_info["articles"].append(article_info)
                
            normalized["chapters"].append(chapter_info)
            
        for i in range(len(normalized["chapters"])):
            for j in range(len(normalized["chapters"][i]["articles"])):
                normalized_result.append({
                    "document_title": normalized["document_title"],
                    "chapter_title": normalized["chapters"][i]["chapter_title"],
                    "article_title": normalized["chapters"][i]["articles"][j]["article_title"],
                    "clause_content": normalized["chapters"][i]["articles"][j]["clause_content"]
                })

    elif level == "chapter":
        normalized = {
            "chapter_title": result.get("title"),
            "articles": []
        }
        for art in result.get("article_titles", []):
            article_info = {
                "article_title": art.get("title"),
                "clause_content": "\n".join([cl.get("content", "") for cl in art.get("all_clause_content", [])])
            }
            normalized["articles"].append(article_info)

        for i in range(len(normalized["articles"])):
            normalized_result.append({
                "document_title": result.get("document_title", ""),
                "chapter_title": normalized["chapter_title"],
                "article_title": normalized["articles"][i]["article_title"],
                "clause_content": normalized["articles"][i]["clause_content"]
            })
    
    elif level == "article":
        normalized = {
            "article_title": result.get("title"),
            "clause_content": "\n".join([cl.get("content", "") for cl in result.get("all_clause_content", [])])
        }
        normalized_result.append({
            "document_title": result.get("document_title", ""),
            "chapter_title": result.get("chapter_title", ""),
            "article_title": normalized["article_title"],
            "clause_content": normalized["clause_content"],
            "demo": "demo"
        })
        
    else:
        return {"result": "No relevant information found."}
    
    return {"result": normalized_result}



# def __chunkChopper(text, max_length=600, overlap=100):
#     words = text
#     chunks = []
#     start = 0
#     separator = ["\n", " ", ".", ",", ";", ":", "!", "?"]
#     while start < len(words):
#         end = min(start + max_length, len(words))
#         # Try to find a separator to split
#         for sep in separator:
#             for i in range(end - 1, start + overlap - 1, -1):
#                 if words[i].endswith(sep):
#                     end = i + 1
#                     break
#             if end != min(start + max_length, len(words)):
#                 break
#         chunk = words[start:end]
#         print(f"Chunk created from word {start} to {end}, length: {len(chunk)}--length of words: {len(words[start:end])}")
#         chunks.append(chunk)
#         if end == len(words):
#             break
#         start += max_length - overlap
#     return chunks
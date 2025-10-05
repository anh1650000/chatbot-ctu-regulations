from .faiss_index import load_faiss_index
from .faiss_index import get_sentence_embedding
from ..db import get_db_connection


def semantic_search(query: str, k: int = 3):
    index, id_mapping = load_faiss_index()
    if not index:
        return [], {}
    
    xq = get_sentence_embedding(query)
    
    D, I = index.search(xq, k)
    return D, I[0], id_mapping


def fetch_results(I, id_mapping):
    results = []
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        for i in I:
            meta = id_mapping.get(str(i))
            if meta:
                cursor.execute("""
                    SELECT d.title AS document_title,
                    c.title AS chapter_title,
                    a.title AS article_title,
                    group_concat(cl.content SEPARATOR '\n') as all_clauses_content
                    FROM documents d
                    JOIN chapters c ON d.doc_id = c.doc_id
                    JOIN articles a ON c.chapter_id = a.chapter_id
                    JOIN clauses cl ON a.article_id = cl.article_id
                    WHERE d.doc_id = %s AND c.chapter_id = %s AND a.article_id = %s
                """, 
                (meta['doc_id'], meta['chapter_id'], meta['article_id']))
                
                row = cursor.fetchone()
                if row:
                    results.append({
                        "document_title": row["document_title"],
                        "chapter_title": row["chapter_title"],
                        "article_title": row["article_title"],
                        "clause_content": row["all_clauses_content"]
                    })

        return {
            "result": results,
        } or {"result": "No relevant information found."}
    except Exception as e:
        return {"result": e}
    
    finally:
        cursor.close()
        conn.close()    
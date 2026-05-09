from .faiss_index import load_faiss_index
from .faiss_index import get_sentence_embedding
from ..db import get_db_connection
from .query_preprocessing import remove_accent

# Import _remove_accent từ query_preprocessing
import unicodedata

def semantic_search(query: str, k: int = 3):
    """
    Search trên CẢ 2 FAISS index (có dấu và không dấu) rồi merge kết quả
    
    Args:
        query: Query string (có dấu)
        k: Số kết quả mỗi index trả về
        
    Returns:
        distances, ids, id_mapping (đã merge và deduplicate)
    """
    index_accent, index_no_accent, id_mapping = load_faiss_index()
    if not index_accent or not index_no_accent:
        return [], [], {}
    
    # Search trên index CÓ DẤU
    xq_accent = get_sentence_embedding(query)  # Query có dấu
    D_accent, I_accent = index_accent.search(xq_accent, k)
    
    # Search trên index KHÔNG DẤU
    query_no_accent = remove_accent(query)  # Bỏ dấu query
    xq_no_accent = get_sentence_embedding(query_no_accent)
    D_no_accent, I_no_accent = index_no_accent.search(xq_no_accent, k)
    
    # Merge kết quả với score fusion
    merged_ids, merged_distances = _merge_search_results(
        I_accent[0], D_accent[0],
        I_no_accent[0], D_no_accent[0],
        k=k
    )
    
    return merged_distances, merged_ids, id_mapping


def _merge_search_results(ids_accent, scores_accent, ids_no_accent, scores_no_accent, k=5):
    """
    Merge kết quả từ 2 index với weight score fusion
    
    Strategy: 
    -có dấu: weight 0.6
    -không dấu: weight 0.4
    -deduplicate và sort theo combined score
    """
    WEIGHT_ACCENT = 0.6
    WEIGHT_NO_ACCENT = 0.4
    
    combined_scores = {}
    
    # Process results từ index có dấu
    for idx, (doc_id, score) in enumerate(zip(ids_accent, scores_accent)):
        doc_id = int(doc_id)
        combined_scores[doc_id] = combined_scores.get(doc_id, 0) + (score * WEIGHT_ACCENT)
    
    # Process results từ index không dấu
    for idx, (doc_id, score) in enumerate(zip(ids_no_accent, scores_no_accent)):
        doc_id = int(doc_id)
        combined_scores[doc_id] = combined_scores.get(doc_id, 0) + (score * WEIGHT_NO_ACCENT)
    
    # Sort theo combined score (descending)
    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Lấy top k
    top_results = sorted_results[:k]
    
    merged_ids = [doc_id for doc_id, _ in top_results]
    merged_distances = [score for _, score in top_results]
    
    return merged_ids, merged_distances


def fetch_results(I, id_mapping):
    """
    fetch clause details (1 clause = 1 chunk)
    returns: {"result": [list of clauses]} or {"result": []} if error
    """
    results = []
    conn = get_db_connection()
    
    #connection error
    if conn is None:
        print("❌ ERROR: Database connection failed in fetch_results")
        return {"result": []}
    
    cursor = conn.cursor(dictionary=True, buffered=True)
    
    try:
        for i in I:
            meta = id_mapping.get(str(i))
            if not meta:
                print(f"⚠️ Warning: No metadata found for ID {i}")
                continue
            
            cursor.execute("""
                SELECT d.title AS document_title,
                c.title AS chapter_title,
                a.title AS article_title,
                cl.content AS clause_content
                FROM documents d
                JOIN chapters c ON d.doc_id = c.doc_id
                JOIN articles a ON c.chapter_id = a.chapter_id
                JOIN clauses cl ON a.article_id = cl.article_id
                WHERE d.doc_id = %s AND c.chapter_id = %s AND a.article_id = %s AND cl.clause_id = %s
            """, 
            (meta['doc_id'], meta['chapter_id'], meta['article_id'], meta['clause_id']))
            
            row = cursor.fetchone()
            if row:
                # Format thống nhất với BM25: "doc → chapter → article\ncontent"
                doc_title = row["document_title"]
                chapter_title = row["chapter_title"]
                article_title = row["article_title"]
                clause_content = row["clause_content"]
                
                # Tạo danh sách titles (bỏ trùng)
                titles = [doc_title]
                if chapter_title != doc_title:
                    titles.append(chapter_title)
                if article_title not in titles:
                    titles.append(article_title)
                
                # Format: "doc → chapter → article\ncontent"
                formatted_chunk = " → ".join(titles) + "\n" + clause_content.lower()
                
                results.append(formatted_chunk)
            else:
                print(f"⚠️ Warning: No data found for clause_id={meta.get('clause_id')}")

        return {"result": results}
        
    except Exception as e:
        print(f"❌ ERROR in fetch_results: {e}")
        import traceback
        traceback.print_exc()
        return {"result": []}
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()    
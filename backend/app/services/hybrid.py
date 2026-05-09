import hashlib
from .search_services import semantic_search, fetch_results
from .bm25_index import load_bm25_index, search_bm25
from .utils import count_tokens_simple

# =========================
#  ⚙️ CẤU HÌNH THAM SỐ
# =========================
_TOP_K_FAISS = 12        # FAISS lấy 12 vector gần nhất
_TOP_N_BM25 = 10         # BM25 lấy 10 kết quả chính xác nhất
_MAX_CONTEXT_TOKENS = 3000  # Giảm từ 4500 → 3000 để giảm noise
_K_RANK = 50
_WEIGHT_BM25 = 0.6 
_WEIGHT_FAISS = 1 - _WEIGHT_BM25  
_MIN_SCORE_THRESHOLD = 0.005  # Lọc chunks có score quá thấp


def _hash_text(text: str):
    """Tạo khóa duy nhất cho mỗi đoạn văn để tránh trùng."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _extract_content(text: str) -> str:
    """
    Trích xuất nội dung thuần (bỏ dòng đầu tiên chứa titles) để làm key hash.
    
    Format thống nhất: "doc → chapter → article\ncontent"
    
    → Lấy tất cả sau dấu \n đầu tiên (= content thuần)
    """
    lines = text.split('\n', 1)  # Split tối đa 1 lần
    
    if len(lines) >= 2:
        # Lấy phần content (sau dòng title)
        content = lines[1]
    else:
        # Fallback: lấy toàn bộ nếu chỉ có 1 dòng
        content = text
    
    return content.strip().lower()


def hybrid_search(query: str):

    result = {}

    # ----- BM25 -----
    bm25 = load_bm25_index()
    if bm25:
        result_bm25, scores, meta_bm25 = search_bm25(query, top_n=_TOP_N_BM25)
    else:
        result_bm25, meta_bm25 = [], []

    # ----- FAISS -----
    distances, ids, id_mapping = semantic_search(query, k=_TOP_K_FAISS)
    result_faiss = fetch_results(ids, id_mapping).get("result", [])
    # fetch_results đã trả về format thống nhất: "doc → chapter → article\ncontent"

    # ----- RRF FUSION -----
    if result_bm25 and result_faiss:
        fused_results = _reciprocal_rank_fusion(result_bm25, result_faiss)
        result = {"result": fused_results}
    else:
        result = {"result": "No relevant information found."}

    return result


def _reciprocal_rank_fusion(results_bm25, results_faiss):
    """Kết hợp kết quả bằng Reciprocal Rank Fusion."""
    combined_scores = {}
    combined_results = {}

    # ---- BM25 ----
    for rank, doc in enumerate(results_bm25):
        # Dùng content thuần làm key để có thể match với FAISS
        content_key = _extract_content(doc)
        key = _hash_text(content_key)
        score = (1 / (_K_RANK + rank + 1)) * _WEIGHT_BM25
        combined_scores[key] = combined_scores.get(key, 0) + score
        # Lưu doc gốc (có metadata) để hiển thị
        if key not in combined_results:
            combined_results[key] = doc

    # ---- FAISS ----
    for rank, doc in enumerate(results_faiss):
        # Dùng content thuần làm key để có thể match với BM25
        content_key = _extract_content(doc)
        key = _hash_text(content_key)
        score = (1 / (_K_RANK + rank + 1)) * _WEIGHT_FAISS
        combined_scores[key] = combined_scores.get(key, 0) + score
        # Ưu tiên format của FAISS (đẹp hơn với →)
        if key not in combined_results:
            combined_results[key] = doc
        # Nếu đã có từ BM25, thay bằng format FAISS
        else:
            combined_results[key] = doc

    # ---- SẮP XẾP ----
    sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    # ---- GỘP THEO CONTEXT TOKEN ----
    top_results = []
    current_tokens = 0

    for key, score in sorted_docs:
        # Lọc chunks có score quá thấp
        if score < _MIN_SCORE_THRESHOLD:
            continue
            
        doc_text = combined_results[key]
        
        token_count = count_tokens_simple(doc_text)
        if current_tokens + token_count > _MAX_CONTEXT_TOKENS:
            break

        top_results.append(doc_text)
        current_tokens += token_count

    return top_results

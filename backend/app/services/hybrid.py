from .search_services import semantic_search, fetch_results
from .bm25_index import load_bm25_index, search_bm25

_top_k = 7
_top_n = 7
_k_hybrid = 5
_weigh_bm25 = 0.6
_weigh_faiss = 1 - _weigh_bm25
_k_rank = 60

def hybrid_search(query: str):
    global _top_k, _top_n, _k_hybrid
    result = {}
    
    # ----RANK BM25-----
    bm25 = load_bm25_index()
    if bm25:
        result_bm25, scores, meta_data_bm25 = search_bm25(query, top_n=_top_n)

    # ----RANK FAISS-----             
    result_faiss = []
    distances, ids, id_mapping = semantic_search(query, k=_top_k)
    result_faiss_list = fetch_results(ids, id_mapping).get("result", [])
    for item in result_faiss_list:
        faiss_article_title = item.get("article_title", "").lower()
        faiss_clause_content = item.get("clause_content", "").lower()
        result_faiss.append(faiss_article_title + " \n " + faiss_clause_content)

    # ----RECIPROCAL RANKING FUSION-----
    if result_bm25 and result_faiss:
        result = reciprocal_rank_fusion(result_bm25, result_faiss, k_hybrid=_k_hybrid)

    return result or {"result": "No relevant information found."}

def reciprocal_rank_fusion(results_bm25, results_faiss, k_hybrid=4):

    global _weigh_bm25, _weigh_faiss, _k_rank
    
    combined_scores = {}
    combined_results = {}
    
    
    # Process BM25 results
    for rank, doc in enumerate(results_bm25):
        score = (1 / (_k_rank + rank + 1)) * _weigh_bm25
        combined_scores[doc] = combined_scores.get(doc, 0) + score
        combined_results[doc] = doc
    
    # Process FAISS results
    for rank, doc in enumerate(results_faiss):
        score = (1 / (_k_rank + rank + 1)) * _weigh_faiss
        combined_scores[doc] = combined_scores.get(doc, 0) + score
        combined_results[doc] = doc
    # Sort by combined scores
    sorted_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Select top k_hybrid results
    top_results = []
    for doc, _ in sorted_docs[:k_hybrid]:
        top_results.append(combined_results[doc])

    return top_results

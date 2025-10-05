from fastapi import APIRouter
from ..services.utils import search_nested_structure, normalize_nested_structure
from ..services.hybrid import hybrid_search
# from ..services.search_services import semantic_search, fetch_results
#----demo rankbm25
# from ..services.bm25_index import load_bm25_index, search_bm25
# from ..services.utils import load_data, text_splitter
router = APIRouter()

@router.get("/search")
def search(query: str):
    # result = {}
    query = query.lower()
    
    # First, try querying the nested structure
    # data = search_nested_structure(query)
    # if data and data["level"] != "none" and data["level"] != "error":
    #     result = normalize_nested_structure(data)
    #     return result

    # If no result from nested structure, try hybrid search between BM25 and FAISS
    result = hybrid_search(query)

    return result or {"result": "No relevant information found."}
    

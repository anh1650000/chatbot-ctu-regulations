from fastapi import APIRouter
from ..services.utils import search_nested_structure, normalize_nested_structure
from ..services.search_services import semantic_search, fetch_results
router = APIRouter()

@router.get("/search")
def search(query: str):
    result = {}
    query = query.lower()
    
    data = search_nested_structure(query)
    
    if data and data["level"] != "none" and data["level"] != "error":
        result = normalize_nested_structure(data)
        return result

    ids, id_mapping = semantic_search(query, k=3)
    result = fetch_results(ids, id_mapping)
    
    return result or {"result": "No relevant information found."}
    

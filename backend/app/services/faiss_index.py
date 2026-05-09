import json
import faiss
import numpy as np
from .embeddings import load_model

_faiss_index_accent = None 
_faiss_index_no_accent = None
_id_mapping = None

model = load_model()

def load_faiss_index():
    
    """Load FAISS index có dấu và k dấu"""
    global _faiss_index_accent, _faiss_index_no_accent, _id_mapping
    
    if _faiss_index_accent is None or _faiss_index_no_accent is None or _id_mapping is None:
        
        _faiss_index_accent = faiss.read_index("data/index.faiss")
        _faiss_index_no_accent = faiss.read_index("data/index_none_accent.faiss")
        
        # Load ID mapping
        with open("data/id_mapping.json", "r", encoding="utf-8") as f:
            _id_mapping = json.load(f)  
            
    return _faiss_index_accent, _faiss_index_no_accent, _id_mapping

def get_sentence_embedding(sentence: str):
    embedding = model.encode(sentence, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
    # Reshape if single sentence
    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1) #convert (dim, 1) to (1, dim) - dim: 768 (bkai-foundation-models/vietnamese-bi-encoder)
    return embedding

# if __name__ == "__main__":
#     from .search_services import fetch_results  # Import để lấy content từ DB
    
#     faiss_index_accent, faiss_index_no_accent, id_mapping = load_faiss_index()
#     query = "ĐTBCHK 3.6 trở lên được cộng bao nhiêu điểm rèn luyện?"

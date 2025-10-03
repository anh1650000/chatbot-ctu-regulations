import json
import faiss
import numpy as np

from .embeddings import load_model

_faiss_index = None
_id_mapping = None

model = load_model()

def load_faiss_index():
    global _faiss_index, _id_mapping
    if _faiss_index is None or _id_mapping is None:
        _faiss_index = faiss.read_index("data/index.faiss")
        with open("data/id_mapping.json", "r", encoding="utf-8") as f:
            _id_mapping = json.load(f)
            
    return _faiss_index, _id_mapping

def get_sentence_embedding(sentence: str):
    embedding = model.encode(sentence, convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
    # Reshape if single sentence
    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1) #convert (dim, 1) to (1, dim) dim:384 (default of all-MiniLM-L6-v2)
    return embedding

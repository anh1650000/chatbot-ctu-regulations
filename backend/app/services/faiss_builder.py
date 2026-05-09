from .utils import load_data, text_splitter
from .faiss_index import get_sentence_embedding
from .query_preprocessing import remove_accent
import faiss
import json


class FAISSIndex:
    def __init__(self):
        self.index = None
        self.index_no_accent = None
        self.meta_data = list()
    
    def __add_embeddings(self, embeddings):
        self.index.add(embeddings)


    def get_faiss_index(self):
        data = load_data()
        
        #----------CREATE INDEX OF EMBEDDINGS LEVEL CLAUSE--------------
        if data:
            text_chunks, meta_data = text_splitter(data)
            
            # Build index accent
            sentence_embeddings = get_sentence_embedding(text_chunks)
            dimension = sentence_embeddings.shape[1]
            
            self.index = build_faiss_index(sentence_embeddings, dimension=dimension)
            self.meta_data = meta_data
            
            # Build index non-accent
            text_chunks_non_accent = [remove_accent(chunk) for chunk in text_chunks]
            sentence_embeddings_non_accent = get_sentence_embedding(text_chunks_non_accent)
            self.index_no_accent = build_faiss_index(sentence_embeddings_non_accent, dimension=dimension)

        # Save FAISS index accent
        faiss.write_index(self.index, "data/index.faiss")
        
        # Save FAISS index non-accent
        faiss.write_index(self.index_no_accent, "data/index_none_accent.faiss")

        # Create ID mapping
        id_mapping = {
            i: meta
            for i, meta in enumerate(meta_data)
        }
        with open("data/id_mapping.json", "w", encoding="utf-8") as f:
            json.dump(id_mapping, f, ensure_ascii=False, indent=4)
            
        # -----------------------------------------------------------------------
        return self.index


def build_faiss_index(embeddings, dimension):
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        return index   
    
if __name__ == "__main__":
    faiss_module = FAISSIndex()
    index = faiss_module.get_faiss_index()


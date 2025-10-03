from ..db import get_db_connection
import numpy as np
from ..services.utils import load_data, text_splitter
from ..services.utils import get_sentence_embedding
import faiss



class FAISSIndex:
    def __init__(self):
        self.index = None
        # self.meta_data = list()
    
    def __add_embeddings(self, embeddings):
        self.index.add(embeddings)


    def get_faiss_index(self):
        data = load_data()
        
        #----------CREATE INDEX OF EMBEDDINGS LEVEL ARTICLE--------------
        # uncomment to create new file index and mapping
        if data:
            text_chunks, meta_data = text_splitter(data)
            sentence_embeddings = get_sentence_embedding(text_chunks)
            dimension = sentence_embeddings.shape[1]
            self.index = build_faiss_index(sentence_embeddings, dimension=dimension)
            # self.meta_data = meta_data
        
        # Save the FAISS index
        ''' faiss.write_index(self.index, "data/index.faiss")'''

            # Create ID mapping
        '''id_mapping = {
            i: meta
            for i, meta in enumerate(meta_data)
        }
        with open("data/id_mapping.json", "w", encoding="utf-8") as f:
            json.dump(id_mapping, f, ensure_ascii=False, indent=4)'''
        # ------------------------------------------------------------------------------
        
        return self.index


def build_faiss_index(embeddings, dimension):
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        return index   
    
if __name__ == "__main__":
    faiss_module = FAISSIndex()
    index, meta_data = faiss_module.get_faiss_index()
    # xq = get_sentence_embedding("cách quy đổi thang điểm 10 sang thang điểm 4")
    # D, I = index.search(np.array([xq]), 5)
    # for i in I[0]:
    #     print(f"Content: {faiss_module.text_chunks[i]}\n")


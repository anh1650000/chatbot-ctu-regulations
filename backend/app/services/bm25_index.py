from .utils import load_data, text_splitter
from rank_bm25 import BM25Okapi

_bm25 = None
_corpus = None
_meta_data = None

def load_bm25_index():
    global _bm25, _corpus, _meta_data

    if _bm25 is not None and _corpus is not None:
        return _bm25

    _corpus, _meta_data = text_splitter(load_data())

    tokenized_corpus = [doc.split(" ") for doc in _corpus]
    _bm25 = BM25Okapi(tokenized_corpus)
    
    return _bm25

def search_bm25(query, top_n=3):
    global _bm25, _corpus, _meta_data
    
    tokenized_query = query.split(" ")
    scores = _bm25.get_scores(tokenized_query)
    return _bm25.get_top_n(tokenized_query, _corpus, n=top_n), scores, _meta_data


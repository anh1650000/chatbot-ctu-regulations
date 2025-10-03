from ..db import get_db_connection
from rank_bm25 import BM25Okapi

_corpus = None

def build_bm25_index(corpus):
    global _corpus
    _corpus = corpus
    return _corpus
    tokenized_corpus = [doc.split(" ") for doc in _corpus]
    return BM25Okapi(tokenized_corpus)

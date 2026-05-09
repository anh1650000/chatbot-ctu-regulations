import re
import unicodedata
import json
from underthesea import word_tokenize

_SYNONYMS = None

def _clean_text(text: str) -> str:
    text = text.lower().strip()
    text = unicodedata.normalize("NFC", text)
    # Giữ chữ tiếng Việt, số và dấu chấm trong số thập phân
    text = re.sub(r"[^\w\s.]", " ", text)  # Xóa ký tự đặc biệt trừ .
    text = re.sub(r"\.(?=\s|$)", " ", text)  # Xóa dấu . cuối câu/trước space
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _segment_words(text: str) -> str:
    return " ".join(word_tokenize(text))

def _normalize_text(text: str) -> list[str]:
    global _SYNONYMS
    if _SYNONYMS is None:
        with open("data/synonyms.json", "r", encoding="utf-8") as f:
            _SYNONYMS = json.load(f)
    texts = [text]
    for key, synonyms in _SYNONYMS.items():
        if key in text:
            for s in synonyms:
                texts.append(text.replace(key, s))
    return list(set(texts))

def _remove_stopwords(text: str) -> str:
    with open("data/vie_stopwords.txt", "r", encoding="utf-8") as f:
        stopwords = set(f.read().splitlines())
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return " ".join(filtered_words)

def remove_accent(text: str) -> str:
    # Xử lý ký tự đ/Đ riêng vì không phải combining character
    text = text.replace('đ', 'd').replace('Đ', 'D')
    # Bỏ dấu các ký tự khác
    text = unicodedata.normalize("NFD", text)
    text = ''.join([char for char in text if not unicodedata.combining(char)])
    text = unicodedata.normalize("NFC", text)
    return text

def preprocess_query_for_bm25(query: str) -> str:
    query = _clean_text(query)
    query = _segment_words(query)
    query = _remove_stopwords(query)
    return query
    
def preprocess_query_for_faiss(query: str) -> list[str]:
    query = _clean_text(query)
    # query = _segment_words(query)
    query = _remove_stopwords(query)
    queries = _normalize_text(query)  # Return list
    queries = [remove_accent(q) for q in queries]  # Bỏ dấu cho tất cả
    return queries  # Return list[str]

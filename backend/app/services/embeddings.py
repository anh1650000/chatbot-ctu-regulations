
import torch
from sentence_transformers import SentenceTransformer

# gpu or cpu

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"   
    # model name
    MODEL_NAME = "all-MiniLM-L6-v2"
    return SentenceTransformer(MODEL_NAME, device=device)



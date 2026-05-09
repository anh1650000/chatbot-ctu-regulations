
import torch
from sentence_transformers import SentenceTransformer

# gpu or cpu

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"   
    
    # Model name - BKAI Vietnamese bi-encoder
    # BKAI Foundation Models - specialized for Vietnamese
    # Model: bkai-foundation-models/vietnamese-bi-encoder (768 dim)
    MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
    
    return SentenceTransformer(MODEL_NAME, device=device)


import os
from dotenv import load_dotenv
from pathlib import Path
import torch
from langchain_ollama.llms import OllamaLLM

# Load .env file from backend directory
env_path = "backend/.env"
load_dotenv(dotenv_path=env_path)

_model = None
_device = "cuda" if torch.cuda.is_available() else "cpu"

# Load model
def get_model():
    global _model, _device
    
    if _model is not None:
        return _model
     
    model_name = os.getenv("MODEL_NAME")
    if _model is None:
        # Optimize for faster streaming
        _model = OllamaLLM(model=model_name, 
                           options={
                               "temperature": 0.3,
                               "top_p": 0.5,
                               "top_k": 30,
                               "num_predict": 1024,      # Tăng lên để không bị cắt câu trả lời
                               "num_ctx": 8192,           # Context window
                               "num_thread": 8,           # Sử dụng 8 CPU threads
                               "num_gpu": 1,              # Dùng GPU nếu có (NVIDIA)
                               "repeat_penalty": 1.1,     # Tránh lặp từ
                           }
                           )
        
    return _model

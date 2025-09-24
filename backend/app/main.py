from fastapi import APIRouter, FastAPI
from underthesea import word_tokenize
from .db import get_db_connection
from fastapi.routing import APIRouter
from .router.searchs import router as search_router

app = FastAPI()
app.include_router(search_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"Hello": "World"}


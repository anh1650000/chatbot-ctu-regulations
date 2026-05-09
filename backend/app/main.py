from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .routers.ask import router as ask_router
from .routers.users import router as users_router
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên specify chính xác
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ask_router, prefix="/api")
app.include_router(users_router, prefix="/api/user")

# Mount static files (CSS, JS)
web_dir = os.path.join(os.path.dirname(__file__), "..", "..", "Web")
app.mount("/Web", StaticFiles(directory=web_dir), name="web")

# Serve index.html at root
@app.get("/")
async def read_root():
    index_path = os.path.join(web_dir, "index.html")
    return FileResponse(index_path)

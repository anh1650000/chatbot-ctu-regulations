from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..services.conversation_service import (
    get_user_conversations,
    save_conversation as save_conv_service,
    delete_user_conversations as delete_conv_service
)
from ..services.user_service import (
    register_user,
    login_user,
    check_username_exists
)

router = APIRouter()

# ==============================
# Pydantic Models
# ==============================
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class MessageCreate(BaseModel):
    user_id: int
    conversation_id: Optional[int] = None
    message: str
    reply: str

# ==============================
# User Authentication Endpoints
# ==============================

@router.post("/register")
async def register(user: UserRegister):
    """Đăng ký user mới"""
    try:
        user_id = register_user(user.username, user.password)
        
        return {
            "message": "User registered successfully",
            "user_id": user_id
        }
    
    except Exception as e:
        if "already exists" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(user: UserLogin):
    """Đăng nhập user"""
    try:
        user_data = login_user(user.username, user.password)
        
        return {
            "message": "Login successful",
            "user": user_data
        }
    
    except Exception as e:
        if "Invalid username or password" in str(e):
            raise HTTPException(status_code=401, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check_username")
async def check_username(username: str):
    """Kiểm tra username đã tồn tại chưa"""
    try:
        exists = check_username_exists(username)
        return {"exists": exists}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# Conversation Endpoints
# ==============================

@router.post("/conversation")
async def save_conversation(msg: MessageCreate):
    """Lưu conversation và messages vào database"""
    try:
        conversation_id = save_conv_service(
            user_id=msg.user_id,
            conversation_id=msg.conversation_id,
            message=msg.message,
            reply=msg.reply
        )
        
        return {
            "message": "Conversation saved successfully",
            "conversation_id": conversation_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation/{user_id}")
async def get_conversations(user_id: int, limit: int = 50):
    """Lấy lịch sử conversations với messages của user"""
    try:
        return get_user_conversations(user_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversation/{user_id}")
async def delete_user_conversations(user_id: int):
    """Xóa toàn bộ lịch sử conversations và messages của user"""
    try:
        deleted_count = delete_conv_service(user_id)
        
        return {
            "message": f"Deleted {deleted_count} conversations",
            "deleted_count": deleted_count
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

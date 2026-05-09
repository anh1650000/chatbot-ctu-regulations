"""
Service để xử lý user authentication và quản lý user
"""
from ..db import get_db_connection
import bcrypt
from typing import Dict, Any


def register_user(username: str, password: str) -> int:
    """
    Đăng ký user mới
    
    Args:
        username: Tên đăng nhập
        password: Mật khẩu (plain text)
    
    Returns:
        user_id của user vừa tạo
    
    Raises:
        Exception: Nếu username đã tồn tại hoặc có lỗi
    """
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Check if username exists
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            raise Exception("Username already exists")
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        cursor.execute(
            "INSERT INTO users (username, user_password) VALUES (%s, %s)",
            (username, hashed_password.decode('utf-8'))
        )
        conn.commit()
        
        user_id = cursor.lastrowid
        return user_id
    
    except Exception as e:
        conn.rollback()
        raise Exception(f"Registration failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def login_user(username: str, password: str) -> Dict[str, Any]:
    """
    Đăng nhập user
    
    Args:
        username: Tên đăng nhập
        password: Mật khẩu (plain text)
    
    Returns:
        Dict chứa user info: {id, username, created_at}
    
    Raises:
        Exception: Nếu username/password sai
    """
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get user
        cursor.execute(
            "SELECT user_id, username, user_password, created_at FROM users WHERE username = %s",
            (username,)
        )
        db_user = cursor.fetchone()
        
        if not db_user:
            raise Exception("Invalid username or password")
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), db_user['user_password'].encode('utf-8')):
            raise Exception("Invalid username or password")
        
        return {
            "id": db_user['user_id'],
            "username": db_user['username'],
            "created_at": db_user['created_at'].isoformat()
        }
    
    except Exception as e:
        raise Exception(f"Login failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def check_username_exists(username: str) -> bool:
    """
    Kiểm tra username đã tồn tại chưa
    
    Args:
        username: Tên đăng nhập cần check
    
    Returns:
        True nếu username đã tồn tại, False nếu chưa
    """
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        exists = cursor.fetchone() is not None
        
        return exists
    
    except Exception as e:
        raise Exception(f"Check failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()

"""
Service để xử lý conversation history
"""
from ..db import get_db_connection
from typing import Optional, List, Dict, Any


def get_conversation_history_text(user_id: int, conversation_id: int, limit: int = 20) -> str:
    """
    Lấy N messages gần nhất từ conversation để đưa vào prompt LLM
    
    Args:
        user_id: ID của user (để verify ownership)
        conversation_id: ID của conversation
        limit: Số lượng messages cần lấy (default 20)
    
    Returns:
        String format: "User: ...\nBot: ...\nUser: ...\nBot: ..."
    """
    conn = get_db_connection()
    if not conn:
        return ""
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Lấy 20 messages gần nhất từ bảng messages
        cursor.execute(
            """
            SELECT sender, message_text, created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (conversation_id, limit)
        )
        
        messages = cursor.fetchall()
        messages.reverse()  # Đảo ngược để hiển thị từ cũ → mới
        
        # Format thành text
        history_lines = []
        for msg in messages:
            role = "User" if msg['sender'] == 'user' else "Bot"
            history_lines.append(f"{role}: {msg['message_text']}")
        
        return "\n".join(history_lines)
    
    except Exception as e:
        print(f"Error loading conversation history: {e}")
        return ""
    finally:
        cursor.close()
        conn.close()


def get_user_conversations(user_id: int, limit: int = None) -> Dict[str, Any]:
    """
    Lấy messages của user (từ 1 conversation duy nhất)
    
    Args:
        user_id: ID của user
        limit: Giới hạn số messages (None = lấy toàn bộ)
    
    Returns:
        Dict chứa user_id, total, conversations (1 conversation với messages)
    """
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed")
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Lấy conversation_id của user (mỗi user chỉ có 1 conversation)
        cursor.execute(
            """
            SELECT conversation_id, started_at
            FROM conversations
            WHERE user_id = %s
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (user_id,)
        )
        
        conversation = cursor.fetchone()
        
        if not conversation:
            return {
                "user_id": user_id,
                "total": 0,
                "conversations": []
            }
        
        conv_id = conversation['conversation_id']
        
        # Lấy messages (toàn bộ hoặc có limit)
        if limit:
            # Lấy N messages gần nhất, nhưng trả về theo thứ tự cũ → mới
            cursor.execute(
                """
                SELECT sender, message_text, created_at
                FROM (
                    SELECT sender, message_text, created_at
                    FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                ) AS recent_messages
                ORDER BY created_at ASC
                """,
                (conv_id, limit)
            )
        else:
            # Không có LIMIT - lấy toàn bộ theo thứ tự cũ → mới
            cursor.execute(
                """
                SELECT sender, message_text, created_at
                FROM messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC
                """,
                (conv_id,)
            )
        
        messages = cursor.fetchall()
        # Không cần reverse nữa vì query đã đúng thứ tự
        
        return {
            "user_id": user_id,
            "total": 1,
            "conversations": [{
                'conversation_id': conv_id,
                'started_at': conversation['started_at'].isoformat() if conversation['started_at'] else None,
                'messages': [
                    {
                        'sender': msg['sender'],
                        'message': msg['message_text'],
                        'created_at': msg['created_at'].isoformat() if msg['created_at'] else None
                    }
                    for msg in messages
                ]
            }]
        }
    
    except Exception as e:
        raise Exception(f"Fetch failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def save_conversation(user_id: int, conversation_id: Optional[int], message: str, reply: str) -> int:
    """
    Lưu conversation và messages vào database
    
    Args:
        user_id: ID của user
        conversation_id: ID của conversation (None để tạo mới)
        message: Tin nhắn từ user
        reply: Câu trả lời từ bot
    
    Returns:
        conversation_id (mới hoặc existing)
    """
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed")
    
    try:
        cursor = conn.cursor()
        
        # Tạo conversation mới hoặc dùng existing
        if not conversation_id:
            cursor.execute(
                "INSERT INTO conversations (user_id) VALUES (%s)",
                (user_id,)
            )
            conn.commit()
            conversation_id = cursor.lastrowid
        
        # Lưu user message
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender, message_text) VALUES (%s, %s, %s)",
            (conversation_id, 'user', message)
        )
        
        # Lưu bot reply
        cursor.execute(
            "INSERT INTO messages (conversation_id, sender, message_text) VALUES (%s, %s, %s)",
            (conversation_id, 'bot', reply)
        )
        
        conn.commit()
        
        return conversation_id
    
    except Exception as e:
        conn.rollback()
        raise Exception(f"Save failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def delete_user_conversations(user_id: int) -> int:
    """
    Xóa toàn bộ messages của user (giữ lại conversation cho tương lai)
    
    Args:
        user_id: ID của user
    
    Returns:
        Số lượng messages đã xóa
    """
    conn = get_db_connection()
    if not conn:
        raise Exception("Database connection failed")
    
    try:
        # Ping để kiểm tra connection còn sống ko
        conn.ping(reconnect=True)
        
        cursor = conn.cursor()
        
        # Lấy conversation_id của user
        cursor.execute(
            "SELECT conversation_id FROM conversations WHERE user_id = %s",
            (user_id,)
        )
        conv_ids = [row[0] for row in cursor.fetchall()]
        
        deleted_count = 0
        if conv_ids:
            # Chỉ xóa messages, GIỮ LẠI conversation
            placeholders = ','.join(['%s'] * len(conv_ids))
            cursor.execute(
                f"DELETE FROM messages WHERE conversation_id IN ({placeholders})",
                conv_ids
            )
            deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        
        return deleted_count
    
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Delete failed: {str(e)}")
    finally:
        cursor.close()
        conn.close()
        conn.rollback()


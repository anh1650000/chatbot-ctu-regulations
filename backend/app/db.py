from mysql.connector import connect
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env file từ thư mục backend
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def get_db_connection():
    try:
        connection = connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

import sqlite3
import os
from contextlib import contextmanager

DATABASE_PATH = os.getenv('DATABASE_PATH', 'database.db')

@contextmanager
def get_connection():
    """Context manager para conexão com banco de dados"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

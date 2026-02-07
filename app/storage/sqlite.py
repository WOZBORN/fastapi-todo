import sqlite3
import os
from pathlib import Path


# Путь к базе данных
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_PATH = BASE_DIR / "data" / "app.db"


def get_db_connection():
    """
    Создаёт соединение с SQLite базой данных
    """
    # Проверяем, что папка data существует
    os.makedirs(DATABASE_PATH.parent, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Возвращает словари вместо кортежей
    return conn
from .sqlite import get_db_connection


def init_database():
    """
    Инициализирует базу данных: создаёт таблицу notes, если её нет
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Создаём таблицу notes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            todo_id INTEGER,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_public BOOLEAN DEFAULT 1
        )
        ''')

        conn.commit()
        print(f"✅ База данных инициализирована успешно")

    except Exception as e:
        print(f"❌ Ошибка при инициализации БД: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


# Для быстрого тестирования
if __name__ == "__main__":
    init_database()
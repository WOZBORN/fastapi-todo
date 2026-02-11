"""
Репозиторий заметок с поддержкой SQLite и fallback в памяти.
"""
from typing import Optional, List, Dict
import datetime

# Безопасный импорт SQLite слоя (не падает, если модули отсутствуют)
try:
    # ИСПРАВЛЕНИЕ 3: Исправлено имя функции с get_conn на get_db_connection
    # (соответствует реальному имени в модуле app.storage.sqlite)
    from app.storage.sqlite import get_db_connection
    from app.storage.init_db import init_db
except Exception:
    # ИСПРАВЛЕНИЕ 3: Изменено имя переменной для соответствия импорту
    get_db_connection = None
    init_db = None


class NotesRepository:
    """
    Интерфейс репозитория заметок.
    Все методы должны быть реализованы в дочерних классах.
    """

    def create_note(
            self,
            todo_id: Optional[int],
            text: str,
            is_public: bool = True
    ) -> Dict:
        raise NotImplementedError()

    def list_notes(
            self,
            todo_id: Optional[int] = None,
            public_only: bool = False
    ) -> List[Dict]:
        raise NotImplementedError()

    def get_note(self, note_id: int) -> Optional[Dict]:
        raise NotImplementedError()

    def delete_note(self, note_id: int) -> bool:
        raise NotImplementedError()


class InMemoryNotesRepository(NotesRepository):
    """
    Fallback-реализация репозитория в памяти.
    Используется, когда SQLite недоступен.
    """

    def __init__(self):
        # Хранилище заметок: {id: заметка}
        self._notes: Dict[int, Dict] = {}
        # Счётчик для генерации уникальных ID
        self._id_counter: int = 1

    def create_note(
            self,
            todo_id: Optional[int],
            text: str,
            is_public: bool = True
    ) -> Dict:
        note_id = self._id_counter
        self._id_counter += 1

        note = {
            "id": note_id,
            "todo_id": todo_id,
            "text": text,
            "is_public": is_public,
            "created_at": datetime.datetime.now().isoformat()
        }
        self._notes[note_id] = note
        return note

    def list_notes(
            self,
            todo_id: Optional[int] = None,
            public_only: bool = False
    ) -> List[Dict]:
        notes = []
        for note in self._notes.values():
            # Фильтр по задаче
            if todo_id is not None and note["todo_id"] != todo_id:
                continue
            # Фильтр только публичные
            if public_only and not note["is_public"]:
                continue
            notes.append(note)
        return notes

    def get_note(self, note_id: int) -> Optional[Dict]:
        return self._notes.get(note_id)

    def delete_note(self, note_id: int) -> bool:
        if note_id in self._notes:
            del self._notes[note_id]
            return True
        return False


class SQLiteNotesRepository(NotesRepository):
    """
    Реализация репозитория с использованием SQLite.
    Работает только если доступен слой БД от Антона Борисовича.
    """

    def __init__(self):
        # ИСПРАВЛЕНИЕ 3: Исправлена проверка переменной
        if get_db_connection is None:
            raise RuntimeError("SQLite layer is not available")

        # Инициализация БД при первом использовании
        if init_db is not None:
            init_db()

    def create_note(
            self,
            todo_id: Optional[int],
            text: str,
            is_public: bool = True
    ) -> Dict:
        # ИСПРАВЛЕНИЕ 3: Исправлен вызов функции
        conn = get_db_connection()
        cursor = conn.cursor()

        # ИСПРАВЛЕНИЕ 1: Убрана передача created_at из кода
        # Таблица имеет DEFAULT CURRENT_TIMESTAMP для столбца created_at
        # База данных автоматически установит текущую дату/время
        cursor.execute(
            """
            INSERT INTO notes (todo_id, text, is_public)
            VALUES (?, ?, ?)
            """,
            (
                todo_id,
                text,
                int(is_public)  # SQLite хранит булевы как 0/1
                # ИСПРАВЛЕНИЕ 1: created_at удалён из параметров
            )
        )
        conn.commit()

        # Получение созданной заметки по последнему сгенерированному ID
        note_id = cursor.lastrowid
        return self.get_note(note_id)

    def list_notes(
            self,
            todo_id: Optional[int] = None,
            public_only: bool = False
    ) -> List[Dict]:
        # ИСПРАВЛЕНИЕ 3: Исправлен вызов функции
        conn = get_db_connection()
        cursor = conn.cursor()

        # Базовый запрос
        # ИСПРАВЛЕНИЕ 2а: Упрощён запрос с использованием * вместо перечисления полей
        query = """
            SELECT * FROM notes
            WHERE 1=1
        """
        params = []

        # Фильтр по задаче
        if todo_id is not None:
            query += " AND todo_id = ?"
            params.append(todo_id)

        # Фильтр только публичные
        if public_only:
            query += " AND is_public = 1"

        # Сортировка по дате создания (новые сверху)
        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Преобразование строк в словари
        notes = []
        for row in rows:
            # ИСПРАВЛЕНИЕ 2: Используем индексы для доступа к полям
            # Порядок полей: id, todo_id, text, is_public, created_at
            notes.append({
                "id": row[0],
                "todo_id": row[1],
                "text": row[2],
                "is_public": bool(row[3]),  # Преобразуем 0/1 в bool
                "created_at": row[4]
            })

        return notes

    def get_note(self, note_id: int) -> Optional[Dict]:
        # ИСПРАВЛЕНИЕ 3: Исправлен вызов функции
        conn = get_db_connection()
        cursor = conn.cursor()

        # ИСПРАВЛЕНИЕ 2: Упрощён запрос с использованием *
        cursor.execute(
            """
            SELECT * FROM notes
            WHERE id = ?
            """,
            (note_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        # ИСПРАВЛЕНИЕ 2: Используем индексы для доступа к полям
        return {
            "id": row[0],
            "todo_id": row[1],
            "text": row[2],
            "is_public": bool(row[3]),
            "created_at": row[4]
        }

    def delete_note(self, note_id: int) -> bool:
        # ИСПРАВЛЕНИЕ 3: Исправлен вызов функции
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()

        # rowcount > 0 означает, что запись была найдена и удалена
        return cursor.rowcount > 0


def get_notes_repository() -> NotesRepository:
    """
    Фабрика репозиториев.
    Автоматически выбирает реализацию:
    - SQLiteNotesRepository, если доступен слой БД
    - InMemoryNotesRepository в противном случае (fallback)

    :return: Экземпляр репозитория заметок
    """
    # Проверяем доступность SQLite
    # ИСПРАВЛЕНИЕ 3: Исправлена проверка переменной
    if get_db_connection is not None:
        try:
            # Проверяем работоспособность подключения
            # ИСПРАВЛЕНИЕ 3: Исправлен вызов функции
            conn = get_db_connection()
            conn.cursor().execute("SELECT 1")
            return SQLiteNotesRepository()
        except Exception:
            # Любая ошибка -> используем fallback
            pass

    # Fallback к in-memory реализации
    return InMemoryNotesRepository()


"""
Репозиторий заметок с поддержкой SQLite и fallback в памяти.
"""
from typing import Optional, List, Dict, Union
import datetime

# Безопасный импорт SQLite слоя (не падает, если модули отсутствуют)
try:
    from app.storage.sqlite import get_conn
    from app.storage.init_db import init_db
except Exception:
    get_conn = None
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
        if get_conn is None:
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
        conn = get_conn()
        cursor = conn.cursor()

        # Вставка новой заметки
        cursor.execute(
            """
            INSERT INTO notes (todo_id, text, is_public, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                todo_id,
                text,
                int(is_public),  # SQLite хранит булевы как 0/1
                datetime.datetime.now().isoformat()
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
        conn = get_conn()
        cursor = conn.cursor()

        # Базовый запрос
        query = """
            SELECT id, todo_id, text, is_public, created_at
            FROM notes
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
            notes.append({
                "id": row[0],
                "todo_id": row[1],
                "text": row[2],
                "is_public": bool(row[3]),  # Преобразуем 0/1 в bool
                "created_at": row[4]
            })

        return notes

    def get_note(self, note_id: int) -> Optional[Dict]:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, todo_id, text, is_public, created_at
            FROM notes
            WHERE id = ?
            """,
            (note_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "todo_id": row[1],
            "text": row[2],
            "is_public": bool(row[3]),
            "created_at": row[4]
        }

    def delete_note(self, note_id: int) -> bool:
        conn = get_conn()
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
    if get_conn is not None:
        try:
            # Проверяем работоспособность подключения
            conn = get_conn()
            conn.cursor().execute("SELECT 1")
            return SQLiteNotesRepository()
        except Exception:
            # Любая ошибка → используем fallback
            pass

    # Fallback к in-memory реализации
    return InMemoryNotesRepository()


from fastapi import APIRouter, HTTPException, Depends
from app.repositories.notes import get_notes_repository, NotesRepository

router = APIRouter(prefix="/notes", tags=["notes"])


# Dependency для внедрения репозитория
def get_repo() -> NotesRepository:
    return get_notes_repository()


@router.post("/")
def create_note(
        todo_id: int | None = None,
        text: str = "",
        is_public: bool = True,
        repo: NotesRepository = Depends(get_repo)
):
    if not text.strip():
        raise HTTPException(400, "Text cannot be empty")

    note = repo.create_note(todo_id, text, is_public)
    return note


@router.get("/")
def list_notes(
        todo_id: int | None = None,
        public_only: bool = False,
        repo: NotesRepository = Depends(get_repo)
):
    return repo.list_notes(todo_id, public_only)


@router.get("/{note_id}")
def get_note(note_id: int, repo: NotesRepository = Depends(get_repo)):
    note = repo.get_note(note_id)
    if note is None:
        raise HTTPException(404, "Note not found")
    return note


@router.delete("/{note_id}")
def delete_note(note_id: int, repo: NotesRepository = Depends(get_repo)):
    if not repo.delete_note(note_id):
        raise HTTPException(404, "Note not found")
    return {"success": True}
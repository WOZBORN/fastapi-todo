# Проект FastAPI TODO
Проект представляет собой API для управления списком задач.

## Установка зависимостей
```bash
pip install -r requirements.txt
```

## Запуск приложения
```bash
uvicorn main:app --reload
```
#  Notes Repository

Слой доступа к данным для заметок с поддержкой **безопасного импорта** и **автоматического fallback**.

---

##  Назначение

Абстрагирует работу с заметками от бизнес-логики API. Позволяет:
- Работать с заметками через единый интерфейс
- Автоматически переключаться между SQLite и in-memory хранилищем
- Не зависеть от готовности слоя БД при разработке

---

##  Архитектура

NotesRepository (интерфейс)
SQLiteNotesRepository  используется, если доступен слой БД
InMemoryNotesRepository  fallback при отсутствии БД

> **Безопасный импорт**:  
> ```python
> try:
>     from app.storage.sqlite import get_conn
> except Exception:
>     get_conn = None  # ← проект не упадёт без слоя БД
> ```

---

##  Интерфейс

```python
class NotesRepository:
    def create_note(
        self,
        todo_id: int | None,
        text: str,
        is_public: bool = True
    ) -> dict: ...

    def list_notes(
        self,
        todo_id: int | None = None,
        public_only: bool = False
    ) -> list[dict]: ...

    def get_note(self, note_id: int) -> dict | None: ...

    def delete_note(self, note_id: int) -> bool: ...
from app.repositories.notes import get_notes_repository

## Автоматический выбор реализации
repo = get_notes_repository()

# Создание заметки
note = repo.create_note(
    todo_id=123,
    text="Важная заметка",
    is_public=True
)

# Получение списка
public_notes = repo.list_notes(public_only=True)

# Удаление
repo.delete_note(note_id=42)



    `Тестирование`
python -m pytest tests/test_notes_repo.py -v
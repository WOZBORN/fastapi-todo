from fastapi import APIRouter, HTTPException
from typing import Optional

try:
    from repositories.notes_repository import NotesRepository
    from schemas.notes import NoteCreate
except ImportError:
    from pydantic import BaseModel
    from typing import Optional as Opt

#Заглушка для теста
    class NoteCreate(BaseModel):
        todo_id: Opt[int] = None
        text: str
        is_public: bool = True


    class NotesRepository:
        def __init__(self):
            self.notes = []
            self.next_id = 1

        async def create(self, text: str, is_public: bool, todo_id: Opt[int] = None):
            note = {
                "id": self.next_id,
                "text": text,
                "is_public": is_public,
                "todo_id": todo_id
            }
            self.notes.append(note)
            self.next_id += 1
            return note

        async def get_all(self, todo_id=None, public_only=False):
            result = self.notes
            if todo_id is not None:
                result = [n for n in result if n["todo_id"] == todo_id]
            if public_only:
                result = [n for n in result if n["is_public"]]
            return result

        async def get_by_id(self, note_id: int):
            for note in self.notes:
                if note["id"] == note_id:
                    return note
            return None

        async def delete(self, note_id: int):
            for i, note in enumerate(self.notes):
                if note["id"] == note_id:
                    self.notes.pop(i)
                    return True
            return False
#Роутер
router = APIRouter(prefix="/notes", tags=["notes"])
repo = NotesRepository()


@router.post("/")
async def create_note(note: NoteCreate):
    if note.todo_id:
        try:
            pass
        except:
            pass

    created_note = await repo.create(
        text=note.text,
        is_public=note.is_public,
        todo_id=note.todo_id
    )
    return created_note


@router.get("/")
async def get_notes(
        todo_id: Optional[int] = None,
        public_only: bool = False
):
    notes = await repo.get_all(
        todo_id=todo_id,
        public_only=public_only
    )
    return notes


@router.get("/{note_id}")
async def get_note(note_id: int):
    note = await repo.get_by_id(note_id)
    if note is None:
        raise HTTPException(404, "Заметка не найдена")
    return note


@router.delete("/{note_id}")
async def delete_note(note_id: int):
    deleted = await repo.delete(note_id)
    return {"deleted": deleted}
from pydantic import BaseModel
from typing import Optional


class NoteCreate(BaseModel):
    todo_id: Optional[int] = None
    text: str
    is_public: bool = True


class NoteResponse(BaseModel):
    id: int
    todo_id: Optional[int] = None
    text: str
    is_public: bool

 class DeleteResponse(BaseModel):
    deleted: bool
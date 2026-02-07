from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.storage import init_database


# Инициализируем базу данных при старте приложения
init_database()


class TaskModel(BaseModel):
    name: str
    description: str
    status: list[str]
    done: bool = False

tasks = []
# 12345

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"message": "To Do API!"}

@app.get("/tasks")
def get_tasks(status: str = None):
    if status:
        return [task for task in tasks if task.status == status]
    return tasks

@app.post("/tasks")
def post_tasks(task: TaskModel):
    tasks.append(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_tasks(task_id: int):
    tasks.pop(task_id)
    return {"message": f"задача {task_id} удалена"}

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from uuid import uuid4

app = FastAPI(title="Tasks API")

class TaskIn(BaseModel):
    title: str = Field(..., min_length=1, strip_whitespace=True)
    completed: bool = False

class Task(TaskIn):
    id: str

DB: dict[str, Task] = {}

@app.get("/tasks/", response_model=List[Task])
def list_tasks():
    return list(DB.values())

@app.post("/tasks/", response_model=Task, status_code=201)
def create_task(payload: TaskIn):
    task_id = str(uuid4())
    task = Task(id=task_id, **payload.model_dump())
    DB[task_id] = task
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    if task_id not in DB:
        raise HTTPException(status_code=404, detail="Task not found")
    del DB[task_id]
    return

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    if task_id not in DB:
        raise HTTPException(status_code=404, detail="Task not found")
    return DB[task_id]

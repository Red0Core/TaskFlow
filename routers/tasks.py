from fastapi import Depends, APIRouter, HTTPException
from utils import get_task_or_404, get_user_or_404
from schemas import TaskCreate, TaskResponse, TaskUpdate, TaskPut
from database import get_db, User, Task
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/users/{user_id}/tasks", response_model=list[TaskResponse])
async def get_tasks(user_id: int, is_completed: bool | None = None, db: Session = Depends(get_db)):
    user = get_user_or_404(user_id, db)

    query = db.query(Task).filter(Task.user_id == user.id)
    if is_completed is not None:
        query = query.filter(Task.is_completed == is_completed)
    
    return query.all()

@router.post("/users/{user_id}/tasks", status_code=201)
async def add_task(user_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    user = get_user_or_404(user_id, db)

    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=user_id  # Привязываем задачу к пользователю
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

@router.get("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_one_task(user_id: int, task_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    task = get_task_or_404(task_id, user_id, db)
    
    return task

@router.patch("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: int,
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    get_user_or_404(user_id, db)
    task = get_task_or_404(task_id, user_id, db)

    # Обновляем только переданные поля
    update_data = task_update.model_dump(exclude_unset=True)  # Игнорируем не переданные поля
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task

@router.put("/users/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def put_task(
    user_id: int,
    task_id: int,
    task_data: TaskPut,
    db: Session = Depends(get_db)
):
    get_user_or_404(user_id, db)
    task = get_task_or_404(task_id, user_id, db)

    # Полное обновление всех полей
    task.title = task_data.title
    task.description = task_data.description
    task.is_completed = task_data.is_completed

    db.commit()
    db.refresh(task)
    return task

@router.delete("/users/{user_id}/tasks/{task_id}", status_code=204)
async def delete_task(user_id: int, task_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    task = get_task_or_404(task_id, user_id, db)
    
    db.delete(task)
    db.commit()
    return

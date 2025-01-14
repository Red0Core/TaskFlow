from fastapi import Depends, APIRouter, Query
from utils import get_task_or_404
from schemas import TaskCreate, TaskResponse, TaskUpdate, TaskPut
from database import get_db, User, Task
from sqlalchemy.orm import Session
from routers.auth import get_current_user

router = APIRouter()

@router.get(
        "/tasks",
        response_model=list[TaskResponse],
        summary="Получение всех задач",
        description="Возвращает список всех задач, доступных пользователю."
    )
async def get_tasks(
    is_completed: bool | None = Query(
        None,
        description="Фильтр задач по статусу выполнения (True - выполненные, False - невыполненные)"
    ),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.user_id == user.id)
    if is_completed is not None:
        query = query.filter(Task.is_completed == is_completed)
    
    return query.all()

@router.post(
        "/tasks",
        status_code=201,
        summary="Создание новой задачи",
        description="Создаёт новую задачу и добавляет её в базу данных."
    )
async def add_task(task: TaskCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=user.id  # Привязываем задачу к пользователю
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

@router.get(
        "/tasks/{task_id}",
        response_model=TaskResponse,
        summary="Получение задачи по ID",
        description="Возвращает данные задачи по её уникальному идентификатору."
    )
async def get_one_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, user.id, db)
    
    return task

@router.patch(
        "/tasks/{task_id}",
        response_model=TaskResponse,
        summary="Обновление задачи частично",
        description="Обновляет данные задачи частично по её уникальному идентификатору."
    )
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_task_or_404(task_id, user.id, db)

    # Обновляем только переданные поля
    update_data = task_update.model_dump(exclude_unset=True)  # Игнорируем не переданные поля
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task

@router.put(
        "/tasks/{task_id}", 
        response_model=TaskResponse,
        summary="Обновление задачи",
        description="Обновляет данные задачи по её уникальному идентификатору."
    )
async def put_task(
    task_id: int,
    task_data: TaskPut,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = get_task_or_404(task_id, user.id, db)

    # Полное обновление всех полей
    task.title = task_data.title
    task.description = task_data.description
    task.is_completed = task_data.is_completed

    db.commit()
    db.refresh(task)
    return task

@router.delete(
        "/tasks/{task_id}",
        status_code=204,
        summary="Удаление задачи",
        description="Удаляет задачу поеё уникальному идентификатору."
    )
async def delete_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = get_task_or_404(task_id, user.id, db)
    
    db.delete(task)
    db.commit()
    return

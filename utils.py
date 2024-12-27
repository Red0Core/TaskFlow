import bcrypt
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import User, Task

def get_user_or_404(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_task_or_404(task_id: int, user_id: int, db: Session):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

def hash_password(password: str) -> str:
    """
    Хэширует пароль с использованием bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Проверяет пароль, сравнивая с хэшем.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
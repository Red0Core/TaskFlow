from fastapi import Depends, HTTPException, APIRouter
from utils import verify_password, hash_password
from schemas import UserInModel, UserModel
from database import get_db, User
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/auth/register", status_code=201)
async def register_user(user: UserInModel, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_db = User(username=user.username, hashed_password=hash_password(user.password))
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return {"username": user_db.username}

@router.post("/auth/login", status_code=200, response_model=UserModel)
async def login_user(user: UserInModel, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == user.username).first()
    if user_db is None or not verify_password(user.password, user_db.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return UserModel(id=user_db.id, tasks=user_db.tasks)
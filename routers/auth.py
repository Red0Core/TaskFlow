from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import database
from sqlalchemy.orm import Session
from pydantic import BaseModel
from schemas import UserInModel, UserModel
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
import bcrypt

SECRET_KEY = "e07688bd48255a3312bce8c105688bbd26b83b7afdf7b70ddd03bb7fd7ace41a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_password = hashed_password.decode('utf8')
    return string_password

def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password)


class UserInDB(BaseModel):
    id: int
    hashed_password: str

class UserIn(BaseModel):
    username: str
    password: str
    
def get_user_from_db_by_username(db: Session, username: str):
    user_db = db.query(database.User).filter(database.User.username == username).first()
    if user_db:
        return user_db

    return None

def get_user_from_db_by_user_id(db: Session, user_id: int):
    user_db = db.query(database.User).filter(database.User.id == user_id).first()
    if user_db:
        return user_db

    return None

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_from_db_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False

    return user

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        # Закладываем не username, а id пользователя
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user_from_db_by_user_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


@router.post("/auth/register", status_code=201)
async def register_user(user: UserIn, db: Session = Depends(database.get_db)):
    existing_user = db.query(database.User).filter(database.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_db = database.User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return {"username": user_db.username}

@router.post("/auth/login", status_code=200, response_model=UserModel)
async def login_user(user: UserInModel, db: Session = Depends(database.get_db)):
    user_db = db.query(database.User).filter(database.User.username == user.username).first()
    if user_db is None or not verify_password(user.password, user_db.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return UserModel(id=user_db.id, tasks=user_db.tasks)

@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(database.get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(user.id)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Закладываем не username, а id пользователя
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    print(Token(access_token=access_token, token_type="bearer"))
    return Token(access_token=access_token, token_type="bearer")

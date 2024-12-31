from operator import ge
from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import database
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr, Field
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from utils import get_password_hash, verify_password

import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

class UserInDB(BaseModel):
    id: int
    hashed_password: str

class UserIn(BaseModel):
    username: str
    password: constr(min_length=8) = Field(
        description="Пароль пользователя. Минимальная длина — 8 символов.",
        min_length=8
    )
    
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

class AccessToken(BaseModel):
    access_token: str
    token_type: str

class RefreshToken(AccessToken):
    refresh_token: str

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

def create_refresh_token(user_id: int):
    expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


@router.post(
        "/auth/register",
        status_code=201,
        summary="Регистрация нового пользователя",
        description="Регистрируется новый пользователь с использованием username и password",
        response_description="В качестве доказательства регистрации запрос возвращает username пользователя"
    )
async def register_user(user: UserIn, db: Session = Depends(database.get_db)):
    existing_user = db.query(database.User).filter(database.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_db = database.User(username=user.username, hashed_password=get_password_hash(user.password))
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return {"username": user_db.username}

@router.post(
        "/token",
        summary="Авторизация пользователя",
        description="Авторизация с выдачей access_token и refresh_token.",
        response_model=RefreshToken,
    )
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(database.get_db)
) -> RefreshToken:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Закладываем не username, а id пользователя
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token, refresh_exp = create_refresh_token(user_id=user.id)

    # Сохраняем refresh_token в базе
    if not db.query(database.RefreshToken).filter(database.RefreshToken.token == refresh_token).first():
        db.add(database.RefreshToken(user_id=user.id, token=refresh_token, expires_at=refresh_exp))
        db.commit()

    return RefreshToken(refresh_token=refresh_token, access_token=access_token, token_type="bearer")

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post(
        "/auth/refresh",
        summary="Обновление access_token",
        description="Отправляя действующий refresh_token, вы получаете новый access_token",
        response_model=AccessToken,
    )
async def refresh_access_token(refresh_token: RefreshTokenRequest, db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(refresh_token.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Проверяем, есть ли такой refresh_token в базе данных
        refresh_token_record = db.query(database.RefreshToken).filter(
            database.RefreshToken.token == refresh_token.refresh_token,
            database.RefreshToken.expires_at > datetime.now()
        ).first()
        if not refresh_token_record:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

        # Генерируем новый access_token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": str(user_id)}, expires_delta=access_token_expires)
        print(f"New access token: {access_token}")
        return AccessToken(access_token=access_token, token_type="bearer")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

@router.post(
        "/auth/logout",
        summary="Выход из сессии",
        description="Клиент полностью выходит из сессии, из базы удаляется refresh_token"
    )
async def logout(
    refresh_token: RefreshTokenRequest,
    db: Session = Depends(database.get_db),
):
    token_record = db.query(database.RefreshToken).filter(database.RefreshToken.token == refresh_token.refresh_token).first()
    if token_record:
        db.delete(token_record)
        db.commit()
    return {"detail": "Successfully logged out"}

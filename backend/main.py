from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, tasks

app = FastAPI()

origins = [
    "http://localhost:80",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:80",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, tags=['Authentication'], prefix="/api")
app.include_router(tasks.router, tags=['Tasks'], prefix="/api")

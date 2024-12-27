from fastapi import FastAPI
from routers import auth, tasks

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)
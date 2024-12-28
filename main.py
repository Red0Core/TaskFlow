from fastapi import FastAPI
from routers import auth, tasks

app = FastAPI()

app.include_router(auth.router, tags=['auth'])
app.include_router(tasks.router, tags=['tasks'])
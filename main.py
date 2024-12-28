from fastapi import FastAPI
from routers import auth, tasks

app = FastAPI()

app.include_router(auth.router, tags=['Authentication'])
app.include_router(tasks.router, tags=['Tasks'])
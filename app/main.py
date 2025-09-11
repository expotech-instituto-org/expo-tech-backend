from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import dotenv_values
from fastapi.responses import RedirectResponse
from app.routes import (
    user
)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(user.router)

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")
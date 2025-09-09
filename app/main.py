from fastapi import FastAPI
from app.routers import users, items
from contextlib import asynccontextmanager
from pymongo import MongoClient
from dotenv import dotenv_values
from app.router import (
    user
)

app = FastAPI()

app.include_router(user.router)
app.include_router(items.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Expo Tech Backend API",
        "swagger": "/docs",
        }
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv()

from app.routes import (
    user_routes,
    project_routes,
    class_routes,
    knowledge_routes,
    review_routes,
    class_routes,
    company_routes,
    exhibition_routes,
    roles_routes
)

app = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/api"  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

route_modules = [
    user_routes,
    exhibition_routes,
    project_routes,
    review_routes,
    roles_routes,
    class_routes,
    company_routes,
    knowledge_routes,
]

for module in route_modules:
    app.include_router(module.router)

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}

print(f"Application available at http://localhost:{os.getenv('PORT', 8000)}/")
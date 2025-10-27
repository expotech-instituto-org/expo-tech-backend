from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
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
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(exhibition_routes.router)
app.include_router(project_routes.router)
app.include_router(review_routes.router)
app.include_router(roles_routes.router)
app.include_router(class_routes.router)
app.include_router(company_routes.router)
app.include_router(knowledge_routes.router)

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}

print(f"Application available at http://localhost:{os.getenv('PORT', 8000)}/")
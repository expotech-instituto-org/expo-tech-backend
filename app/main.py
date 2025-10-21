from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
load_dotenv()

from app.routes import (
    user_routes,
    review_routes,
    class_routes,
    exhibition_routes
)
app = FastAPI()

app.include_router(user_routes.router)
app.include_router(review_routes.router)
app.include_router(class_routes.router)
app.include_router(exhibition_routes.router)


@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")

@app.get("/health", include_in_schema=False)
def health_check():
    return {"status": "ok"}

print(f"Application available at http://localhost:{os.getenv('PORT', 8000)}/")
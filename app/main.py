from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
load_dotenv()

from app.routes import (
    user_routes,
exhibition_routes
)
app = FastAPI()

app.include_router(user_routes.router)
app.include_router(exhibition_routes.router)

@app.get("/", include_in_schema=False)
def read_root():
    return RedirectResponse(url="/docs")
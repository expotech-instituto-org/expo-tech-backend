from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
async def list_users():
    return {"message": "List of users"}

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"message": f"Details of user {user_id}"}
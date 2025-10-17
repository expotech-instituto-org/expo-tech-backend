from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.repository import user_repository
from typing import List, Annotated
from app.model.user import UserModel
from app.dto.user.user_login_dto import UserLogin
from app.routes.security import get_current_user, create_access_token, User, Token

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("", response_model=List[UserModel])
async def list_users():
    try:
        return user_repository.list_all_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}",)# response_model=UserModel)
async def get_user(user_id: str):
    try:
        user = user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=UserModel)
async def create_user(user: UserLogin):
    try:
        return user_repository.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserModel)
async def update_user(user_id: str, user: UserModel):
    try:
        return user_repository.update_user(user_id, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: str):
    try:
        return user_repository.delete_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me/", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    try:
        return {"login": current_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        user = user_repository.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            token = create_access_token(data={"sub": user.login, "scope": " ".join(form_data.scopes)})
            return token
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

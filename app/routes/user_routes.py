import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile, Query, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

from app.repository import user_repository
from typing import List, Annotated, Optional
from app.model.user import UserModel
from app.routes.security import get_current_user, create_access_token, User, Token
import os
from app.service.sendEmail import send_login_token_email
from app.dto.user.user_create_dto import UserCreate

import app.constants as c

logger = logging.getLogger(__name__)



router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("", response_model=List[UserModel])
async def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    name: Optional[str] = Query(None, description="Name of the user"),
    role_id: Optional[str] = Query(None, description="Role ID of the user")
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_USER not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        return user_repository.list_all_users(name, role_id)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.get("/{user_id}", response_model=UserModel)
async def get_user(user_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_READ_USER not in current_user.permissions and user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        user = user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        return user
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.post("", response_model=UserModel)
async def create_user(
    background_tasks: BackgroundTasks,
    user: UserCreate|str = Form(...),
    profile_picture: UploadFile = File(None),
    current_user: Annotated[User | None, Depends(get_current_user)] = None
):# <--- Carinha triste ou brava?
    # HANDLE USER DATA PARSING
    try:
        user_create_data = UserCreate.model_validate_json(user)
    except json.JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format in user_data.")
    except Exception as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

    try:
        permissions = current_user.permissions if current_user else None
        
        user_email = getattr(user_create_data, 'email', 'N/A')
        logger.info(f"[CREATE_USER] Iniciando criação de usuário - Email: {user_email}")
        start_time = datetime.now()
        
        # Verify basic settings before creating the user
        frontend_url = os.getenv("EXPO_FRONT_URL", "")
        if not frontend_url:
            logger.error("[CREATE_USER] EXPO_FRONT_URL não configurado")
            raise RuntimeError("EXPO_FRONT_URL not configured")
        
        logger.info(f"[CREATE_USER] Configurações verificadas - Profile picture: {profile_picture is not None}")
        
        # Create the user first (without email callback)
        logger.info("[CREATE_USER] Chamando user_repository.create_user...")
        create_start = datetime.now()
        created_user = await user_repository.create_user(
            user_create_data, 
            permissions, 
            profile_picture
        )
        create_duration = (datetime.now() - create_start).total_seconds()
        logger.info(f"[CREATE_USER] Usuário criado no banco em {create_duration:.2f}s - User ID: {created_user.id if created_user else 'None'}")
        
        if not created_user:
            logger.error("[CREATE_USER] Falha ao criar usuário - retornou None")
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Not able to create user")
        
        # Generate the token
        logger.info("[CREATE_USER] Gerando token de acesso...")
        token_data = create_access_token(data={
            "sub": created_user.email,
            "user_id": created_user.id,
            "project_id": created_user.project.id if created_user.project else None,
            "scope": "",
            "permissions": created_user.role.permissions,
            "role": {"id": created_user.role.id, "name": created_user.role.name},
            "verified": False
        })
        
        # Prepare the token URL
        frontend_url = frontend_url.rstrip('/')
        token_url = f"{frontend_url}?token={token_data.access_token}"
        user_name = created_user.name if created_user.name else "Olá, visitante!"
        
        # Add the email sending as a background task
        # If it fails, try to delete the user
        def send_email_with_rollback(user_id: str, email: str, name: str, token: str):
            logger.info(f"[BACKGROUND_EMAIL] Iniciando envio de email em background - User ID: {user_id}, Email: {email}")
            email_start = datetime.now()
            try:
                # send_login_token_email(email, name, token)
                email_duration = (datetime.now() - email_start).total_seconds()
                logger.info(f"[BACKGROUND_EMAIL] Email enviado com sucesso em {email_duration:.2f}s - Email: {email}")
            except Exception as e:
                email_duration = (datetime.now() - email_start).total_seconds()
                logger.error(f"[BACKGROUND_EMAIL] Erro ao enviar email após {email_duration:.2f}s - Email: {email}, Erro: {str(e)}")
                try:
                    logger.info(f"[BACKGROUND_EMAIL] Tentando fazer rollback - deletando usuário {user_id}")
                    user_repository.delete_user(user_id)
                    logger.info(f"[BACKGROUND_EMAIL] Rollback realizado com sucesso - Usuário {user_id} deletado")
                except Exception as rollback_error:
                    logger.error(f"[BACKGROUND_EMAIL] Erro ao fazer rollback - User ID: {user_id}, Erro: {str(rollback_error)}")
        
        logger.info(f"[CREATE_USER] Adicionando tarefa de envio de email em background - User ID: {created_user.id}")
        background_tasks.add_task(
            send_email_with_rollback,
            created_user.id,
            created_user.email,
            user_name,
            token_url
        )
        
        total_duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"[CREATE_USER] Processo concluído com sucesso em {total_duration:.2f}s - User ID: {created_user.id}, Email: {created_user.email}")
        
        if created_user is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Not able to create user")
        
        return created_user
    except ValueError as e:
        logger.error(f"[CREATE_USER] Erro de validação: {str(e)}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Not able to create user: {str(e)}")
    except PermissionError as e:
        logger.error(f"[CREATE_USER] Erro de permissão: {str(e)}")
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Not able to create user: {str(e)}")
    except DuplicateKeyError as e:
        logger.error(f"[CREATE_USER] Email duplicado: {str(e)}")
        raise HTTPException(status.HTTP_409_CONFLICT, "Not able to create user: email already exists")
    except RuntimeError as e:
        logger.error(f"[CREATE_USER] Erro de runtime: {str(e)}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Not able to create user: {str(e)}")
    except Exception as e:
        logger.error(f"[CREATE_USER] Erro inesperado: {type(e).__name__}: {str(e)}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Not able to create user: {str(e)}")

@router.put("/{user_id}", response_model=UserModel)
async def update_user(
        user_id: str,
        user: UserModel|str = Form(...),
        profile_picture: UploadFile = File(None),
        current_user: Annotated[User, Depends(get_current_user)] = None
):
    # HANDLE PERMISSIONS
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_UPDATE_USER not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")

    # HANDLE USER DATA PARSING
    try:
        user_update_data = UserModel.model_validate_json(user)
    except json.JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format in user_data.")
    except Exception as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

    # UPDATE USER DATA AND RETURN
    try:
        updated_user = user_repository.update_user(user_id, user_update_data, profile_picture)
        updated_user.id = user_id
        return updated_user
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except PermissionError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(e))
    except DuplicateKeyError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, "Duplicate email")
    except RuntimeError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.patch("/favorite/{project_id}")
async def favorite_project(project_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    try:
        return user_repository.favorite_project(current_user.id, project_id)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@router.delete("/{user_id}", response_model=dict)
async def delete_user(user_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    if c.PERMISSION_DELETE_USER not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    success = user_repository.delete_user(user_id)
    if not success:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return {"message": "User deleted successfully"}

@router.get("/me/", response_model=Optional[User])
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    #TODO: Remover depois
    return current_user



@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = user_repository.authenticate_user(form_data.username, form_data.password)
    if not user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    else:
        token = create_access_token(data={
            "sub": user.email,
            "user_id": user.id,
            "project_id": user.project.id if user.project else None,
            "scope": " ".join(form_data.scopes),
            "permissions": user.role.permissions,
            "role": {"id": user.role.id, "name": user.role.name},
            "verified": True
        })
        return token

@router.post("/verify", response_model=Token)
async def verify_user(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Verify the current user (set verified=True) and return a new access token.
    """
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if current_user.verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "User already verified")
    # Update verified status
    current_user.verified = True
    updated_user = user_repository.update_user(current_user.id, current_user)
    # Generate new access token
    token = create_access_token(data={
        "sub": updated_user.email,
        "user_id": updated_user.id,
        "project_id": updated_user.project.id if updated_user.project else None,
        "scope": "",
        "permissions": updated_user.role.permissions,
        "role": {"id": updated_user.role.id, "name": updated_user.role.name},
        "verified": True
    })
    return token

from typing_extensions import Annotated
from watchfiles import awatch

from app.routes.security import User, get_current_user
from fastapi import APIRouter, HTTPException, status, Query, Depends, status
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File, Form
from app.repository import project_repository
from app.model.project import ProjectModel
from app.dto.project.project_create_dto import ProjectCreateDto
from app.dto.project.project_update_dto import ProjectUpdateDto
from typing import List, Optional
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.errors import InvalidId
from app.repository import exhibition_repository, user_repository
import app.constants as c
import json

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.get("", response_model=List[ProjectModel])
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    exhibition_id: Optional[str] = Query(None, description="ID da exposição para filtrar projetos"),
    project_name: Optional[str] = Query(None, description="Nome do projeto para busca parcial"),
    company_name: Optional[str] = Query(None, description="Nome da empresa para busca parcial")
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_READ_PROJECT not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        projects = project_repository.get_projects_with_filters(
            exhibition_id=exhibition_id,
            project_name=project_name,
            company_name=company_name
        )
        return projects
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID fornecido é inválido"
        )
    except OperationFailure:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do banco de dados"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/{project_id}", response_model=ProjectModel)
async def get_project(
    project_id: str, 
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_READ_PROJECT not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do projeto é obrigatório"
        )
    
    try:
        project = project_repository.get_project_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Projeto não encontrado"
            )
        return project
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do projeto é inválido"
        )
    except OperationFailure:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do banco de dados"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
        
@router.post("", response_model=ProjectModel)
async def create_project(
    project: ProjectCreateDto | str = Form(...),
    logo: UploadFile = File(None),
    images: List[UploadFile] = File(None),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Create a new project.
    - project: ProjectCreateDto data (as JSON string in 'project' form field)
    - logo: Optional logo image file for the project
    - images: Optional list of image files for the project
    """
    # HANDLE PROJECT DATA PARSING
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_CREATE_PROJECT not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        if isinstance(project, str):
            project_create_data = ProjectCreateDto.model_validate_json(project)
        else:
            project_create_data = project
    except json.JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format in project data.")
    except Exception as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
    try:
        return await project_repository.create_project(project_create_data, logo, images)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))

@router.put("/{project_id}", response_model=ProjectModel)
async def update_project(
    project_id: str,
    project: ProjectUpdateDto | str = Form(...),
    logo: UploadFile = File(None),
    images: List[UploadFile] = File(None),
    current_user: Annotated[User, Depends(get_current_user)] = None
):
    """
    Update a project.
    - project_id: ID of the project to update
    - project: ProjectUpdateDto data (as JSON string in 'project' form field)
    - logo: Optional logo image file for the project
    - images: Optional list of image files for the project
    """
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_UPDATE_PROJECT not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    # HANDLE PROJECT DATA PARSING
    try:
        if isinstance(project, str):
            project_update_data = ProjectUpdateDto.model_validate_json(project)
        else:
            project_update_data = project
    except json.JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format in project data.")
    except Exception as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))
    try:
        return await project_repository.update_project(project_id, project_update_data, logo, images)
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, str(e))


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if not current_user.verified:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email not verified")
    if c.PERMISSION_DELETE_PROJECT not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    if not project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do projeto é obrigatório"
        )
    
    try:
        existing_project = project_repository.get_project_by_id(project_id)
        if existing_project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto não encontrado"
            )
        
        result = project_repository.delete_project_by_id(project_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao remover projeto"
            )
        
        return {"message": "Projeto removido com sucesso"}
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do projeto é inválido"
        )
    except OperationFailure:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do banco de dados"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
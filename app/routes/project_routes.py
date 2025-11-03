from typing_extensions import Annotated
from app.routes.security import User, get_current_user
from fastapi import APIRouter, HTTPException, status, Query, Depends, status
from app.repository import project_repository
from app.model.project import ProjectModel
from app.dto.project.project_create_dto import ProjectCreateDto
from app.dto.project.project_update_dto import ProjectUpdateDto
from typing import List, Optional
from pymongo.errors import DuplicateKeyError, OperationFailure
from bson.errors import InvalidId
from app.repository import exhibition_repository, user_repository
import app.constants as c

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
    project: ProjectCreateDto,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_CREATE_PROJECT not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        exhibition = exhibition_repository.get_exhibition_by_id(project.exhibition_id)
        if not exhibition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exposição não encontrada"
            )
        
        if project.expositors:
            for expositor in project.expositors:
                if not user_repository.get_user_by_id(expositor.id):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Usuário expositor não encontrado: {expositor.id}"
                    )
        
        project_model = ProjectModel(
            name=project.name,
            company_name=project.company_name,
            description=project.description,
            coordinates=project.coordinates,
            exhibition_id=project.exhibition_id,
            expositors=[ProjectModel.UserResume(id=exp.id) for exp in project.expositors] if project.expositors else [],
            images=project.images,
            logo=project.logo,
            deactivation_date=None
        )
        
        result = project_repository.add_project(project_model)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao criar projeto. Verifique os dados fornecidos."
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Projeto com dados duplicados já existe"
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

@router.put("/{project_id}", response_model=ProjectModel)
async def update_project(
    project_id: str, 
    project: ProjectUpdateDto,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_UPDATE_PROJECT not in current_user.permissions:
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
        
        update_data = {}
        if project.name is not None:
            update_data["name"] = project.name
        if project.company_name is not None:
            update_data["company_name"] = project.company_name
        if project.description is not None:
            update_data["description"] = project.description
        if project.coordinates is not None:
            update_data["coordinates"] = project.coordinates
        if project.exhibition_id is not None:
            exhibition = exhibition_repository.get_exhibition_by_id(project.exhibition_id)
            if not exhibition:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exposição não encontrada"
                )
            update_data["exhibition_id"] = project.exhibition_id
        if project.expositors is not None:
            if project.expositors:
                for expositor in project.expositors:
                    if not user_repository.get_user_by_id(expositor.id):
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Usuário expositor não encontrado: {expositor.id}"
                        )
            update_data["expositors"] = [ProjectModel.UserResume(id=exp.id) for exp in project.expositors] if project.expositors else []
        if project.images is not None:
            update_data["images"] = project.images
        if project.logo is not None:
            update_data["logo"] = project.logo
        
        updated_fields = {}
        if "name" in update_data:
            updated_fields["name"] = update_data["name"]
        if "company_name" in update_data:
            updated_fields["company_name"] = update_data["company_name"]
        if "description" in update_data:
            updated_fields["description"] = update_data["description"]
        if "coordinates" in update_data:
            updated_fields["coordinates"] = update_data["coordinates"]
        if "exhibition_id" in update_data:
            updated_fields["exhibition_id"] = update_data["exhibition_id"]
        if "expositors" in update_data:
            updated_fields["expositors"] = [exp.model_dump(by_alias=True) for exp in update_data["expositors"]]
        if "images" in update_data:
            updated_fields["images"] = update_data["images"]
        if "logo" in update_data:
            updated_fields["logo"] = update_data["logo"]
        
        result = project_repository.update_project_by_id(project_id, updated_fields)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao atualizar projeto"
            )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados inválidos: {str(e)}"
        )
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

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,   
    current_user: Annotated[User, Depends(get_current_user)] 
):
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
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
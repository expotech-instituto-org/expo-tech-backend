from app.dto.project import project_create_dto
from fastapi import APIRouter, HTTPException, status, Query
from app.repository import project_repository
from app.model.project import ProjectModel
from app.dto.project.project_create_dto import ProjectCreateDto
from app.dto.project.project_update_dto import ProjectUpdateDto
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

@router.get("", response_model=List[ProjectModel])
async def list_projects(
    exhibition_id: Optional[str] = Query(None, description="ID da exposição para filtrar projetos"),
    project_name: Optional[str] = Query(None, description="Nome do projeto para busca parcial"),
    company_name: Optional[str] = Query(None, description="Nome da empresa para busca parcial")
):
    try:
        projects = project_repository.get_projects_with_filters(
            exhibition_id=exhibition_id,
            project_name=project_name,
            company_name=company_name
        )
        
        return projects
    except Exception as e:
        logger.error(f"Erro ao listar projetos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.get("/{project_id}", response_model=ProjectModel)
async def get_project(
    project_id: str, 
):
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
        return project_create_dto
    except Exception as e:
        logger.error(f"Erro ao buscar projeto {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
        
@router.post("", response_model=ProjectModel)
async def create_project(
    project: ProjectCreateDto,
):
    try:
        result = project_repository.add_project(project)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao criar projeto. Verifique os dados fornecidos."
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar projeto: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor ao criar projeto"
        )

@router.put("/{project_id}", response_model=ProjectModel)
async def update_project(
    project_id: str, 
    project: ProjectUpdateDto,
):
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
            update_data["exhibition_id"] = project.exhibition_id
        if project.expositors is not None:
            update_data["expositors"] = [ProjectModel.UserResume(id=exp.id) for exp in project.expositors]
        if project.images is not None:
            update_data["images"] = project.images
        if project.logo is not None:
            update_data["logo"] = project.logo
        
        updated_project = ProjectModel(
            id=project_id,
            name=update_data.get("name", existing_project.name),
            company_name=update_data.get("company_name", existing_project.company_name),
            description=update_data.get("description", existing_project.description),
            coordinates=update_data.get("coordinates", existing_project.coordinates),
            exhibition_id=update_data.get("exhibition_id", existing_project.exhibition_id),
            expositors=update_data.get("expositors", existing_project.expositors),
            images=update_data.get("images", existing_project.images),
            logo=update_data.get("logo", existing_project.logo)
        )
        
        result = project_repository.update_project_by_id(project_id, updated_project)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Falha ao atualizar projeto"
            )
        return result
    except Exception as e:
        logger.error(f"Erro ao atualizar projeto {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,    
):
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
    except Exception as e:
        logger.error(f"Erro ao remover projeto {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
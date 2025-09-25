import uuid
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field
from app.model.role import RoleModel
from app.model.project import ProjectModel

class ProjectResume(ProjectModel):
    class Config:
        fields = {
            "id": ..., 
            "name": ...,
            "logo": ..., 
            "company_name": ...,  
        }
        extra = "ignore"

class CriteriaModel(BaseModel):
    name: str = Field(..., description="Criteria name")
    weight: float = Field(..., description="Criteria weight")

class RoleResume(RoleModel):
    weight: float = Field(..., description="Role weight")
    
    class Config:
        fields = {
            "id": ...,
            "name": ...,
            "weight": ...,
        }
        extra = "ignore"

class ExhibitionModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Exhibition name")
    image: str = Field(..., description="Exhibition image")
    date: date = Field(..., description="Exhibition date")
    description: str = Field(..., description="Exhibition description")
    roles: List[RoleResume] = Field(..., description="Exhibition roles")
    projects: List[ProjectResume] = Field(..., description="Exhibition projects")
    criteria: List[CriteriaModel] = Field(..., description="Exhibition criteria")
    active: bool = Field(..., description="Exhibition active")
    
    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "Tech Corp",
                "image": "https://br.pinterest.com/pin/345088390217105894/",
                "date": "2025-01-01",
                "description": "Exhibition description",
                "roles": [
                    {
                        "_id": str(uuid.uuid4()),
                        "name": "Manager",
                        "weight": 0.8
                    }
                ],
                "projects": [
                    {
                        "_id": str(uuid.uuid4()),
                        "name": "AI Project",
                        "logo": "https://example.com/logo.png",
                        "company_name": "Tech Corp"
                    }
                ],
                "criteria": [
                    {"name": "Innovation", "weight": 0.4},
                    {"name": "Impact", "weight": 0.6}
                ],
                "active": True
            }
        }
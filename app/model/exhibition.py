import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ExhibitionModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Exhibition name")
    image: str = Field(..., description="Exhibition image")
    date: datetime  = Field(..., description="Exhibition date")
    description: str = Field(..., description="Exhibition description")
    active: bool = Field(..., description="Exhibition active")

    class ProjectResume(BaseModel):
        id: Optional[str] = Field(alias="_id")
        name: str = Field(..., description="Exhibition name")
        logo: str = Field(..., description="Exhibition image")
        company_name: str = Field(..., description="Exhibition name")

    projects: List[ProjectResume] = Field(..., description="Exhibition projects")

    class CriteriaModel(BaseModel):
        name: str = Field(..., description="Criteria name")
        weight: float = Field(..., description="Criteria weight")

    criteria: List[CriteriaModel] = Field(..., description="Exhibition criteria")

    class RoleResume(BaseModel):
        id: Optional[str] = Field(alias="_id")
        name: str = Field(..., description="Exhibition name")
        weight: float = Field(..., description="Role weight")
        
    roles: List[RoleResume] = Field(..., description="Exhibition roles")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "Tech Corp",
                "image": "https://br.pinterest.com/pin/345088390217105894/",
                "date":  datetime(2025, 1, 1, 15, 30),
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
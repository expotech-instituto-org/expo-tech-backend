import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ExhibitionModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Exhibition name")
    image: Optional[str] = Field(..., description="Exhibition image")
    start_date: datetime  = Field(..., description="Exhibition start date")
    end_date: datetime  = Field(..., description="Exhibition end date")
    description: Optional[str] = Field(..., description="Exhibition description")
    deactivation_date: Optional[datetime] = Field(..., description="Exhibition deactivation date")

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
        id: str = Field(alias="_id")
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
            }
        }
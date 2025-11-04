import uuid
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ExhibitionModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str = Field(..., description="Exhibition name")
    image: Optional[str] = Field(None, description="Exhibition image")
    start_date: datetime  = Field(..., description="Exhibition start date")
    end_date: datetime  = Field(..., description="Exhibition end date")
    description: Optional[str] = Field(None, description="Exhibition description")
    deactivation_date: Optional[datetime] = Field(None, description="Exhibition deactivation date")
    banners: Optional[List[str]] = Field(None, description="Projects banners")

    class ProjectResume(BaseModel):
        id: Optional[str] = Field(alias="_id")
        name: Optional[str] = Field(None, description="Project name")
        logo: Optional[str] = Field(None, description="Project logo")
        company_name: Optional[str] = Field(None, description="Company name")
        banners: Optional[List[str]] = Field(None, description="Project banners")
        coordinates: Optional[int] = None

    projects: List[ProjectResume] = Field(..., description="Exhibition projects")

    class CriteriaResume(BaseModel):
        name: str = Field(..., description="Criteria name")
        weight: float = Field(..., description="Criteria weight")

    criteria: List[CriteriaResume] = Field(..., description="Exhibition criteria")

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
                "banners": ["banner1.png", "banner2.png"],
                "projects": [
                    {
                        "_id": str(uuid.uuid4()),
                        "name": "AI Project",
                        "logo": "https://example.com/logo.png",
                        "company_name": "Tech Corp",
                        "banners": ["proj_banner1.png", "proj_banner2.png"],
                        "coordinates": 1
                    }
                ],
                "criteria": [
                    {"name": "Innovation", "weight": 0.4},
                    {"name": "Impact", "weight": 0.6}
                ],
            }
        }
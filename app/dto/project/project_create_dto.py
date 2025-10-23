from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class UserIdDto(BaseModel):
    id: str = Field(..., description="User ID")

class ProjectCreateDto(BaseModel):
    name: str = Field(..., min_length=1, description="Project name")
    company_name: str = Field(..., min_length=1, description="Company Name")
    description: str = Field(..., min_length=1, description="Description")
    coordinates: int = Field(..., description="Coordinates")
    exhibition_id: str = Field(..., description="Exhibition id")
    expositors: List[UserIdDto] = Field(..., description="List of expositor users")
    images: List[str] = Field(default=[], description="List of images")
    logo: str = Field(..., description="Logo URL or path")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tech Project",
                "company_name": "Tech Company",
                "description": "descrição do projeto",
                "coordinates": 1,
                "exhibition_id": str(uuid.uuid4()),
                "expositors": [
                    {
                        "id": str(uuid.uuid4())
                    }
                ],
                "images": ["link1", "link2"],
                "logo": "link"
            }
        }


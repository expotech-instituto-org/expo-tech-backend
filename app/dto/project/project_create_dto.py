from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class UserIdDto(BaseModel):
    id: str = Field(..., description="User ID")

class ProjectCreateDto(BaseModel):
    name: str = Field(..., min_length=1, description="Project name")
    company_name: Optional[str] = Field(None, description="Company Name")
    description: str = Field(..., min_length=1, description="Description")
    coordinates: Optional[int] = Field(None, description="Coordinates")
    exhibition_id: str = Field(..., description="Exhibition id")
    expositors: Optional[List[UserIdDto]] = Field(default_factory=list, description="List of expositor users")
    images: Optional[List[str]] = Field(default_factory=list, description="List of images")
    logo: Optional[str] = Field(None, description="Logo URL or path")

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
                "images": ["img1.png", "img2.png"],
                "logo": "logo.png"
            }
        }


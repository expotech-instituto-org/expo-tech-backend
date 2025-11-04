from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class UserIdDto(BaseModel):
    id: str = Field(..., description="User ID")

class ProjectUpdateDto(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Project name")
    company_name: Optional[str] = Field(None, min_length=1, description="Company Name")
    description: Optional[str] = Field(None, min_length=1, description="Description")
    coordinates: Optional[int] = Field(None, description="Coordinates")
    exhibition_id: Optional[str] = Field(None, description="Exhibition id")
    expositors: Optional[List[UserIdDto]] = Field(None, description="List of expositor users")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Tech project",
                "company_name": "Updated Tech company",
                "description": "descrição do projeto atualizado",
                "coordinates": 2,
                "exhibition_id": str(uuid.uuid4()),
                "expositors": [
                    {
                        "id": str(uuid.uuid4())
                    }
                ]
            }
        }

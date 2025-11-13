from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class ProjectCreateDto(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the project")
    name: str = Field(..., min_length=1, description="Project name")
    company_name: Optional[str] = Field(None, description="Company Name")
    description: str = Field(..., min_length=1, description="Description")
    coordinates: Optional[int] = Field(None, description="Coordinates")
    exhibition_id: str = Field(..., description="Exhibition id")
    expositors: Optional[List[str]] = Field(default_factory=list, description="List of expositor users")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tech Project",
                "company_name": "Tech Company",
                "description": "descrição do projeto",
                "coordinates": 1,
                "exhibition_id": str(uuid.uuid4()),
                "expositors": [str(uuid.uuid4())]
            }
        }

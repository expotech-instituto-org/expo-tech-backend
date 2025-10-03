import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.model.role import RoleModel

class ProjectResume(BaseModel):
    id: str = Field(..., alias="_id", description="Project ID")
    name: str = Field(..., description="Project name")
    logo: str = Field(..., description="Project logo URL")
    company_name: str = Field(..., description="Company name associated with the project")
    
    class Config:
        fields = {
            "id": {"description": "Project ID"},
            "name": {"description": "Project name"},
            "logo": {"description": "Project logo URL"},
            "company_name": {"description": "Company name associated with the project"}
        }
        allow_population_by_field_name = True
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "name": "Projeto Incrível"
            }
        }

class ReviewResume(BaseModel):
    project_id: str = Field(..., description="Project ID")
    exhibition_id: str = Field(..., description="Exhibition ID")
    comment: Optional[str] = Field(None, max_length=300, description="Review comment")
    
    class Config:
        fields = {
            "project_id": {"description": "Project ID"},
            "exhibition_id": {"description": "Exhibition ID"},
            "comment": {"description": "Optional comment about the review"}
        }
        allow_population_by_field_name = True
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "project_id": str(uuid.uuid4()),
                "exhibition_id": str(uuid.uuid4()),
                "comment": "Excelente projeto, muito bem executado!"
            }
        }

class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    email: str = Field(...)
    phone: str = Field(...)
    password: str = Field(...)
    role: RoleModel = Field(...)
    profile_picture: Optional[str] = Field(...)
    knowledge: Optional[str] = Field(...)
    age: Optional[int] = Field(...)
    company: Optional[str] = Field(...)
    class_field: Optional[str] = Field(alias="class", default=None)
    project: ProjectResume = Field(...)
    reviews: ReviewResume = Field(...)
    deactivation_date: Optional[datetime] = Field(..., description="Exhibition deactivation date")

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "email": "email@email.com",
                "password": "xxxxxxx",
                "phone": "(11) 99999-9999",
                "role": {
                    "_id": str(uuid.uuid4()),
                    "name": "admin"
                },
                "company": "PicPay",
                "knowledge": "Amigos",
                "age": 30,
                "class": "A",
            }
        }

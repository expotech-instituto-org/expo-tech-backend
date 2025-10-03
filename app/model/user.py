import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.model.role import RoleModel


class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    email: str = Field(...)
    phone: str = Field(...)
    password: str = Field(...)
    name: str = Field(...)
    role: RoleModel = Field(...)
    profile_picture: Optional[str] = Field(...)
    knowledge: Optional[str] = Field(...)
    age: Optional[int] = Field(...)
    company: Optional[str] = Field(...)
    class_field: Optional[str] = Field(alias="class", default=None)

    class ProjectResume(BaseModel):
        id: str = Field(..., alias="_id", description="Project ID")
        name: str = Field(..., description="Project name")
        logo: str = Field(..., description="Project logo URL")
        company_name: str = Field(..., description="Company name associated with the project")

    project: ProjectResume = Field(...)

    class ReviewResume(BaseModel):
        project_id: str = Field(..., description="Project ID")
        exhibition_id: str = Field(..., description="Exhibition ID")
        comment: Optional[str] = Field(None, max_length=300, description="Review comment")

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
                "profile_picture": "https://link-to-image.com/image.png",
                "project": {
                    "_id": str(uuid.uuid4()),
                    "name": "Projeto Exemplo",
                    "company_name": "Tech Corporation"
                },
                "reviews": [
                    {
                        "project_id": str(uuid.uuid4()),
                        "exhibition_id": str(uuid.uuid4()),
                        "comment": "Great project!"
                    }
                ],
                "active": True,
            }
        }

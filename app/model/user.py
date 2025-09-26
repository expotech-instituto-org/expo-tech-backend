import uuid
from typing import Optional
from pydantic import BaseModel, Field
from app.model.role import RoleModel

class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    login: str = Field(...)
    phone: str = Field(...)
    senha: str = Field(...)
    role: RoleModel = Field(...)
    profile_picture: Optional[str] = Field(...)
    knowledge: Optional[str] = Field(...)
    age: Optional[int] = Field(...)
    company: str = Field(...)
    class_field: Optional[str] = Field(alias="class", default=None)
    # project: ProjectModel = Field(...)
    # reviews: ReviewModel = Field(...)
    active: bool = Field(default=True)
    

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "login": "email@email.com",
                "senha": "xxxxxxx"
            }
        }
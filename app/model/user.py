import uuid
from typing import Optional
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    login: str = Field(...)
    senha: str = Field(...)

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "login": "email@email.com",
                "senha": "xxxxxxx"
            }
        }
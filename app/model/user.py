import uuid
from typing import Optional
from pydantic import BaseModel, Field

class UserModel(BaseModel):
    id: Optional[str] = Field(alias="_id")
    email: str = Field(...)

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": str(uuid.uuid4()),
                "email": "email@email.com"
            }
        }

class User(BaseModel):
    email: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "email@email.com"
            }
        }
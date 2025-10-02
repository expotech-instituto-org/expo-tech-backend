from pydantic import BaseModel

class UserLogin(BaseModel):
    login: str
    password: str

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "login": "email@email.com",
                "password": "senha123"
            }
        }
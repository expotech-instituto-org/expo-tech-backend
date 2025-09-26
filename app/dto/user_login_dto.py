from pydantic import BaseModel

class Useremail(BaseModel):
    email: str
    password: str

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "email": "email@email.com",
                "password": "senha123"
            }
        }
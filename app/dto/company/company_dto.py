from pydantic import BaseModel

class CompanyDTO(BaseModel):
    name: str

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example": {
                "name": "Empresa bacanuda"
            }
        }
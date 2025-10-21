from typing import Optional
from app.database import db
from app.model.company import CompanyModel
import uuid

company_collection= db["companies"]

def get_all_company() -> list[CompanyModel]:
    company_cursor = company_collection.find()
    return [CompanyModel (**company_model) for company_model in company_cursor]

def get_company_by_id(company_id: str) -> Optional[CompanyModel]:
    company_data = company_collection.find_one({"_id": company_id})
    if company_data:
        return CompanyModel(**company_data)
    return None

def delete_company(company_id: str) -> bool:
    result = company_collection.delete_one({"_id": company_id})
    return result.deleted_count > 0

def create_company(company_name: str ):
    company_dict = {
        "_id": str(uuid.uuid4()),
        "name": company_name
    }
    result = company_collection.insert_one(company_dict)
    if result.inserted_id:
        return CompanyModel(**company_dict)
    return None

def update_company(update_data: CompanyModel) -> Optional[CompanyModel]:
    result = company_collection.update_one(
        {"_id": update_data.id},
        {"$set": {"name": update_data.name}}
    )
    if result.modified_count > 0:
        updated_company = company_collection.find_one({"_id": update_data.id})
        if updated_company:
            return CompanyModel(**updated_company)
    return None
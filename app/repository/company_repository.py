from typing import Optional
from app.database import db
from app.model.company import CompanyModel
import uuid

companies_collection = db["companies"]

def get_company_by_id(company_id: str) -> Optional[CompanyModel]:
    company_data = companies_collection.find_one({"_id": company_id})
    if company_data:
        return CompanyModel(**company_data)
    return None

def list_all_companies() -> list[CompanyModel]:
    companies_cursor = companies_collection.find()
    return [CompanyModel(**company) for company in companies_cursor]

def create_company(company: CompanyModel) -> Optional[CompanyModel]:
    company_dict = company.model_dump()
    company_dict["_id"] = str(uuid.uuid4())
    result = companies_collection.insert_one(company_dict)
    if result.inserted_id:
        return CompanyModel(**company_dict)
    return None

def update_company(company_id: str, update_data: CompanyModel) -> Optional[CompanyModel]:
    company_dict = update_data.model_dump(exclude_unset=True)
    result = companies_collection.update_one({"_id": company_id}, {"$set": company_dict})
    if result.modified_count > 0:
        updated_company = companies_collection.find_one({"_id": company_id})
        if updated_company:
            return CompanyModel(**updated_company)
    return None

def delete_company(company_id: str) -> bool:
    result = companies_collection.delete_one({"_id": company_id})
    return result.deleted_count > 0

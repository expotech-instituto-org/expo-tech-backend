from app.routes.security import User, get_current_user
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated, List
from app.model.company import CompanyModel
from app.dto.company.company_dto import CompanyDTO
from app.repository.company_repository import (
    get_all_company,
    get_company_by_id,
    create_company,
    update_company,
    delete_company
)
import app.constants as c

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)

# Routes
@router.get("/", response_model=List[CompanyModel])
async def get_all_companies():
    """
    Retrieve all companies
    """
    try:
        companies = get_all_company()
        return companies
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error retrieving companies: {str(e)}")

@router.post("/", response_model=CompanyModel, status_code=status.HTTP_201_CREATED)
async def create_new_company(company_data: CompanyDTO, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Create a new company
    """
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_CREATE_COMPANY not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        new_company = create_company(company_data.name)
        if new_company == None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create company"
            )
        return new_company
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error creating company: {str(e)}")

@router.put("/{company_id}", response_model=CompanyModel)
async def update_existing_company(company_id: str, company_data: CompanyDTO, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Update an existing company
    """
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_UPDATE_COMPANY not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        existing_company = get_company_by_id(company_id)
        if not existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company not found"
            )
        
        updated_company_model = CompanyModel(
            id=existing_company.id,
            name=company_data.name
        )
        
        updated_company = update_company(updated_company_model)
        if not updated_company:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update company"
            )

        return updated_company
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error updating company: {str(e)}")

@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_company(company_id: str, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Delete a company
    """
    if not current_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unauthorized")
    if c.PERMISSION_DELETE_COMPANY not in current_user.permissions:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
    try:
        # First check if company exists
        existing_company = get_company_by_id(company_id)
        if not existing_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Delete company
        success = delete_company(company_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete company"
            )
        
        return None
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error deleting company: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app import schemas
from app.services.admin_service import AdminService, get_admin_service
from app.utils.admin_auth import get_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)]
)

@router.get("/users", response_model=List[schemas.User])
def read_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_service: AdminService = Depends(get_admin_service)
):
    return admin_service.get_all_users(skip=skip, limit=limit)

@router.patch("/users/{user_id}", response_model=schemas.User)
def update_user_details(
    user_id: int,
    user_update: schemas.AdminUserUpdate,
    admin_service: AdminService = Depends(get_admin_service)
):
    updated_user = admin_service.update_user(user_id=user_id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_account(
    user_id: int,
    admin_service: AdminService = Depends(get_admin_service)
):
    success = admin_service.delete_user_account(user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found.",
        )
    return {"message": f"User with id {user_id} and all associated data deleted successfully."}

@router.get("/photos/{category}", response_model=List[schemas.Photo])
def read_all_photos(
    category: str,
    admin_service: AdminService = Depends(get_admin_service)
):
    photos = admin_service.get_all_photos(category=category)
    if photos is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category}' not found.",
        )
    return photos

@router.delete("/photos/{category}/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(
    category: str,
    photo_id: int,
    admin_service: AdminService = Depends(get_admin_service)
):
    success = admin_service.delete_photo(category=category, photo_id=photo_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} in category '{category}' not found.",
        )
    return

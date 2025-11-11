from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.services import admin_service
from app.utils.admin_auth import get_admin_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_admin_user)] # 이 라우터의 모든 경로에 관리자 인증 적용
)

# --- User Management Endpoints ---

@router.get("/users", response_model=List[schemas.User])
def read_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    모든 사용자 목록을 조회합니다. (관리자 전용)
    """
    users = admin_service.get_all_users(db, skip=skip, limit=limit)
    return users

@router.patch("/users/{user_id}", response_model=schemas.User)
def update_user_details(
    user_id: int,
    user_update: schemas.AdminUserUpdate,
    db: Session = Depends(get_db)
):
    """
    사용자의 세부 정보(name, is_active, is_superuser)를 업데이트합니다. (관리자 전용)
    """
    updated_user = admin_service.update_user(db, user_id=user_id, user_update=user_update)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_account(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 계정과 모든 관련 데이터를 삭제합니다. (관리자 전용)
    """
    success = admin_service.delete_user_account(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found.",
        )
    return {"message": f"User with id {user_id} and all associated data deleted successfully."}


# --- Photo Management Endpoints ---

@router.get("/photos/{category}", response_model=List[schemas.Photo])
def read_all_photos(category: str, db: Session = Depends(get_db)):
    """
    카테고리별 모든 사진 목록을 조회합니다. (관리자 전용)
    """
    photos = admin_service.get_all_photos(db, category=category)
    if photos is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category '{category}' not found.",
        )
    return photos

@router.delete("/photos/{category}/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(category: str, photo_id: int, db: Session = Depends(get_db)):
    """
    특정 사진을 DB와 파일 시스템에서 삭제합니다. (관리자 전용)
    """
    success = admin_service.delete_photo(db, category=category, photo_id=photo_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with id {photo_id} in category '{category}' not found.",
        )
    return

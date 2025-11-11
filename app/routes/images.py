from typing import List
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import image_service
from app.utils.security import get_current_user
from app import models, schemas

router = APIRouter(
    prefix="/images",
    tags=["images"],
)

class ImageCategory(str, Enum):
    clothes = "clothes"
    persons = "persons"
    results = "results"

@router.get("/my-clothes", response_model=List[schemas.Photo])
async def get_my_clothes_list(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    현재 로그인된 사용자의 'clothes' 이미지 파일 목록을 반환합니다.
    """
    images = image_service.get_cloth_list_by_user_id(db, current_user.id)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clothes found for the current user.",
        )
    return images

@router.get("/persons", response_model=List[schemas.Photo])
async def get_person_images_list(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    현재 로그인된 사용자의 'persons' 이미지 파일 목록을 반환합니다.
    """
    images = image_service.get_image_list_by_user_id(db, current_user.id)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No images found for the current user.",
        )
    return images

@router.get("/{category}", response_model=List[schemas.Photo])
async def get_public_images_list(category: ImageCategory, db: Session = Depends(get_db)):
    """
    'clothes' 또는 'results' 카테고리의 이미지 파일 목록을 반환합니다.
    'persons'는 이 엔드포인트에서 제외됩니다.
    """
    if category == ImageCategory.persons:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access to person images requires authentication. Please use the /images/persons endpoint.",
        )
    
    images = image_service.get_image_list_by_category(db, category.value)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category specified.",
        )
    return images

@router.get("/{category}/{image_name}")
async def get_image(category: ImageCategory, image_name: str, db: Session = Depends(get_db)):
    """
    지정된 카테고리에서 특정 이름의 이미지 파일을 반환합니다.
    """
    image_path = image_service.get_image_file_path(db, category.value, image_name)

    if image_path is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found or invalid name.",
        )
    
    return FileResponse(image_path)

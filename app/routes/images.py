from typing import List
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import image_service

router = APIRouter(
    prefix="/images",
    tags=["images"],
)

class ImageCategory(str, Enum):
    clothes = "clothes"
    persons = "persons"
    results = "results"

@router.get("/{category}", response_model=List[str])
async def get_images_list(category: ImageCategory, db: Session = Depends(get_db)):
    """
    지정된 카테고리의 이미지 파일 목록을 반환합니다.
    """
    images = image_service.get_image_list_by_category(db, category.value)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category specified.",
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

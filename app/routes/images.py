from typing import List
from enum import Enum
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.services.image_service import ImageService, get_image_service
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

@router.get("/shop-clothes", response_model=List[schemas.Photo])
async def get_shop_clothes_list(image_service: ImageService = Depends(get_image_service)):
    """
    상점(Shop)의 'clothes' 이미지 파일 목록을 반환합니다.
    """
    images = image_service.get_shop_cloth_list()
    if not images:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shop clothes found.",
        )
    return images

@router.get("/my-clothes", response_model=List[schemas.Photo])
async def get_my_clothes_list(
    current_user: models.User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service)
):
    """
    현재 로그인된 사용자의 'clothes' 이미지 파일 목록을 반환합니다.
    """
    images = image_service.get_cloth_list_by_user_id(current_user.id)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clothes found for the current user.",
        )
    return images

@router.get("/persons", response_model=List[schemas.Photo])
async def get_person_images_list(
    current_user: models.User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service)
):
    """
    현재 로그인된 사용자의 'persons' 이미지 파일 목록을 반환합니다.
    """
    images = image_service.get_image_list_by_user_id(current_user.id)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No images found for the current user.",
        )
    return images

@router.get("/{category}", response_model=List[schemas.Photo])
async def get_public_images_list(
    category: ImageCategory,
    image_service: ImageService = Depends(get_image_service)
):
    """
    'clothes' 또는 'results' 카테고리의 이미지 파일 목록을 반환합니다.
    """
    if category == ImageCategory.persons:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access to person images requires authentication. Please use the /images/persons endpoint.",
        )
    
    # Note: This endpoint might be problematic if it returns objects without 'image_url' set 
    # because get_all_photos_by_category just returns DB models.
    # For now we leave it as is, but ideally, it should also enrich with URLs.
    images = image_service.get_image_list_by_category(category.value)
    if images is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid category specified.",
        )
    return images

@router.get("/{category}/{image_name}")
async def get_image(
    category: ImageCategory,
    image_name: str,
    image_service: ImageService = Depends(get_image_service)
):
    """
    지정된 카테고리에서 특정 이름의 이미지 파일을 반환합니다.
    """
    # Mapping category to bucket name
    bucket_map = {
        "clothes": "cloth_photo",
        "persons": "person_photo",
        "results": "result_photo"
    }
    bucket = bucket_map.get(category.value)
    
    if not bucket:
         raise HTTPException(status_code=400, detail="Invalid category")

    url = image_service.image_repo.get_public_url(bucket, image_name)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found or invalid name.",
        )
    
    return RedirectResponse(url)
from typing import List, Optional, Type
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models import Base
from app import schemas
from app.database import get_db
from app.repositories.image_repository import ImageRepository
from app.repositories.photo_repository import PhotoRepository

class ImageService:
    def __init__(self, image_repo: ImageRepository, photo_repo: PhotoRepository):
        self.image_repo = image_repo
        self.photo_repo = photo_repo

    def get_shop_cloth_list(self) -> List[schemas.Photo]:
        """
        상점(SHOP_USER_ID)의 'cloth' 이미지 객체 목록을 가져오는 서비스 함수입니다.
        """
        return self.image_repo.get_shop_cloth_photos()

    def get_cloth_list_by_user_id(self, user_id: int) -> List[schemas.Photo]:
        """
        특정 사용자의 'cloth' 이미지 객체 목록을 가져오는 서비스 함수입니다.
        """
        return self.photo_repo.get_all_cloth_photos_by_user_id(user_id)

    def get_image_list_by_user_id(self, user_id: int) -> Optional[List[schemas.Photo]]:
        """
        특정 사용자의 'person' 이미지 객체 목록을 가져오는 서비스 함수입니다.
        """
        return self.photo_repo.get_all_by_user_id(user_id)

    def get_image_list_by_category(self, category: str) -> Optional[List[schemas.Photo]]:
        """
        카테고리별 이미지 객체 목록을 가져오는 서비스 함수입니다.
        """
        return self.image_repo.get_all_photos_by_category(category)

    def get_image_file_path(self, category: str, image_name: str) -> Optional[str]:
        """
        특정 이미지의 전체 파일 경로를 가져오는 서비스 함수입니다.
        """
        return self.image_repo.get_image_path(category=category, image_name=image_name)

def get_image_service(db: Session = Depends(get_db)) -> ImageService:
    image_repo = ImageRepository(db)
    photo_repo = PhotoRepository(db)
    return ImageService(image_repo, photo_repo)


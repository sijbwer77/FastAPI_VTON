from typing import List, Optional, Type, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Depends

from app.models import Base
from app import schemas
from app.database import get_db
from app.repositories.image_repository import ImageRepository
from app.repositories.photo_repository import PhotoRepository
from app.config import settings

class ImageService:
    def __init__(self, image_repo: ImageRepository, photo_repo: PhotoRepository):
        self.image_repo = image_repo
        self.photo_repo = photo_repo

    def get_shop_cloth_list(self) -> List[Dict[str,Any]]:
        """
        상점(SHOP_USER_ID)의 'cloth' 이미지 객체 목록을 가져오는 서비스 함수입니다.
        """
        admin_id = 1
        return self.get_cloth_list_by_user_id(admin_id)

    def get_cloth_list_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        특정 사용자의 'cloth' 이미지 객체 목록을 가져오는 서비스 함수입니다.
        """
        photos = self.photo_repo.get_all_cloth_photos_by_user_id(user_id)
        result = []
        for photo in photos:
            # 🟢 [핵심] 옷 사진은 'cloth_photo' 버킷에서 URL 생성
            url = self.image_repo.get_public_url("cloth_photo", photo.filename)
            
            result.append({
                "id": photo.id,
                "image_url": url,  # 프론트엔드가 사용할 이미지 주소
                "fitting_type": photo.fitting_type
            })
        return result
        

    def get_image_list_by_user_id(self, user_id: int) -> List[Dict[str, Any]]:
        """
        특정 사용자의 'person' 이미지 객체 목록을 가져오는 서비스 함수입니다.
        """
        photos = self.photo_repo.get_all_by_user_id(user_id)
        
        result = []
        for photo in photos:
            # 🟢 [핵심] 전신 사진은 'person_photo' 버킷에서 URL 생성
            url = self.image_repo.get_public_url("person_photo", photo.filename)
            
            result.append({
                "id": photo.id,
                "image_url": url,
                "uploaded_at": photo.uploaded_at
            })
        return result

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
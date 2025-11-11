from typing import List, Optional, Type
from sqlalchemy.orm import Session

from app.models import Base
from app.repositories.image_repository import ImageRepository
from app.repositories.photo_repository import PhotoRepository

def get_image_list_by_user_id(db: Session, user_id: int) -> Optional[List[Type[Base]]]:
    """
    특정 사용자의 'person' 이미지 객체 목록을 가져오는 서비스 함수입니다.
    """
    photo_repo = PhotoRepository(db)
    photos = photo_repo.get_all_by_user_id(user_id)
    return photos

def get_image_list_by_category(db: Session, category: str) -> Optional[List[Type[Base]]]:
    """
    카테고리별 이미지 객체 목록을 가져오는 서비스 함수입니다.
    """
    image_repo = ImageRepository(db)
    photos = image_repo.get_all_photos_by_category(category)
    return photos


def get_image_file_path(db: Session, category: str, image_name: str) -> Optional[str]:
    """
    특정 이미지의 전체 파일 경로를 가져오는 서비스 함수입니다.
    레포지토리를 호출하여 경로를 검증하고 가져옵니다.
    """
    image_repo = ImageRepository(db)
    return image_repo.get_image_path(category=category, image_name=image_name)

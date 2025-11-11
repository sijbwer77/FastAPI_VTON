from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.image_repository import ImageRepository

def get_image_list_by_category(db: Session, category: str) -> Optional[List[str]]:
    """
    카테고리별 이미지 목록을 가져오는 서비스 함수입니다.
    (Note: This function might need to be adapted if the frontend needs more than just filenames)
    """
    # This function is not directly available in the new repo, but we can simulate it
    # For now, let's assume the public API still just needs filenames.
    # A better approach might be to return full objects and adapt the route's response_model.
    image_repo = ImageRepository(db)
    photos = image_repo.get_all_photos_by_category(category)
    if photos is None:
        return None
    return [photo.filename for photo in photos]


def get_image_file_path(db: Session, category: str, image_name: str) -> Optional[str]:
    """
    특정 이미지의 전체 파일 경로를 가져오는 서비스 함수입니다.
    레포지토리를 호출하여 경로를 검증하고 가져옵니다.
    """
    image_repo = ImageRepository(db)
    return image_repo.get_image_path(category=category, image_name=image_name)

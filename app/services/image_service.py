from typing import List, Optional
from app.repositories import image_repository

def get_image_list_by_category(category: str) -> Optional[List[str]]:
    """
    카테고리별 이미지 목록을 가져오는 서비스 함수입니다.
    레포지토리를 호출하여 데이터를 가져옵니다.
    """
    return image_repository.list_images(category)

def get_image_file_path(category: str, image_name: str) -> Optional[str]:
    """
    특정 이미지의 전체 파일 경로를 가져오는 서비스 함수입니다.
    레포지토리를 호출하여 경로를 검증하고 가져옵니다.
    """
    return image_repository.get_image_path(category, image_name)

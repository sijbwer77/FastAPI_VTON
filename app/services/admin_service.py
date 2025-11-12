import os
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List, Optional, Type

from app import models, schemas
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.image_repository import ImageRepository, CATEGORY_DIRS

class AdminService:
    def __init__(self, user_repo: UserRepository, image_repo: ImageRepository):
        self.user_repo = user_repo
        self.image_repo = image_repo

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[schemas.User]:
        """
        모든 사용자 목록을 가져오는 서비스 함수입니다.
        """
        return self.user_repo.get_all_users(skip=skip, limit=limit)

    def update_user(self, user_id: int, user_update: schemas.AdminUserUpdate) -> schemas.User | None:
        """
        사용자 정보를 업데이트하는 서비스 함수입니다.
        """
        return self.user_repo.update_user_details(user_id=user_id, user_update=user_update)

    def get_all_photos(self, category: str) -> Optional[List[schemas.Photo]]:
        """
        카테고리별 모든 사진 레코드를 가져오는 서비스 함수입니다.
        """
        return self.image_repo.get_all_photos_by_category(category)

    def delete_photo(self, category: str, photo_id: int) -> bool:
        """
        사진을 DB와 파일 시스템에서 모두 삭제하는 서비스 함수입니다.
        """
        deleted_photo_record = self.image_repo.delete_photo_by_id(category, photo_id)
        
        if not deleted_photo_record:
            return False

        try:
            directory = CATEGORY_DIRS.get(category)
            if directory:
                file_path = os.path.join(directory, deleted_photo_record.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting file for photo ID {photo_id}: {e}")
            return True

    def delete_user_account(self, user_id: int) -> bool:
        """
        사용자 계정과 관련된 모든 데이터(파일, DB 레코드)를 삭제합니다.
        """
        user_to_delete = self.user_repo.get_by_id(user_id)
        if not user_to_delete:
            return False

        all_photos = self.image_repo.get_all_photos_for_user(user_id)
        for category, photo_list in all_photos.items():
            directory = CATEGORY_DIRS.get(category)
            if not directory:
                continue
            for photo in photo_list:
                try:
                    file_path = os.path.join(directory, photo.filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

        self.user_repo.delete_user(user_id)
        return True

def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    user_repo = UserRepository(db)
    image_repo = ImageRepository(db)
    return AdminService(user_repo, image_repo)

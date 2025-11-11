import os
import logging
from typing import List, Optional, Type, Dict
from sqlalchemy.orm import Session
from app.models import PersonPhoto, ClothPhoto, ResultPhoto, Base

# --- Constants ---
CATEGORY_DIRS = {
    "clothes": "resources/cloths",
    "persons": "resources/persons",
    "results": "resources/results",
}

CATEGORY_MODELS: Dict[str, Type[Base]] = {
    "clothes": ClothPhoto,
    "persons": PersonPhoto,
    "results": ResultPhoto,
}

# --- Repository Class ---
class ImageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_photos_by_category(self, category: str) -> Optional[List[Type[Base]]]:
        """
        관리자용: 지정된 카테고리의 모든 사진 레코드를 가져옵니다.
        """
        model = CATEGORY_MODELS.get(category)
        if not model:
            return None
        return self.db.query(model).order_by(model.id.desc()).all()

    def delete_photo_by_id(self, category: str, photo_id: int) -> Optional[Type[Base]]:
        """
        관리자용: ID로 특정 사진 레코드를 삭제하고, 삭제된 객체를 반환합니다.
        """
        model = CATEGORY_MODELS.get(category)
        if not model:
            return None
        
        photo_to_delete = self.db.query(model).filter(model.id == photo_id).first()
        
        if photo_to_delete:
            # First, commit the deletion to the database
            self.db.delete(photo_to_delete)
            self.db.commit()
            return photo_to_delete
            
        return None

    def get_all_photos_for_user(self, user_id: int) -> Dict[str, List[Type[Base]]]:
        """
        특정 사용자의 모든 사진 레코드를 카테고리별로 가져옵니다.
        """
        photos = {
            "persons": self.db.query(PersonPhoto).filter(PersonPhoto.user_id == user_id).all(),
            "clothes": self.db.query(ClothPhoto).filter(ClothPhoto.user_id == user_id).all(),
            "results": self.db.query(ResultPhoto).filter(ResultPhoto.user_id == user_id).all(),
        }
        return photos

    def get_image_path(self, category: str, image_name: str) -> Optional[str]:
        """
        DB를 확인하여 카테고리와 이미지 이름이 유효한지 검증하고,
        유효하다면 전체 파일 경로를 반환합니다.
        """
        target_dir = CATEGORY_DIRS.get(category)
        model = CATEGORY_MODELS.get(category)
        if not target_dir or not model:
            return None

        # 경로 조작 공격 방지를 위한 보안 검사
        if ".." in image_name or "/" in image_name or "\\" in image_name:
            logging.warning(f"Invalid image name requested: {image_name}")
            return None

        record_exists = self.db.query(model).filter(model.filename == image_name).first()
        if not record_exists:
            return None

        image_path = os.path.join(target_dir, image_name)

        if not os.path.isfile(image_path):
            logging.warning(f"DB record exists for {image_path}, but the file is missing.")
            return None
        
        return image_path

from sqlalchemy.orm import Session
from app import models
from datetime import datetime

class UploadRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_person_photo(self, user_id: int, filename_original: str, filename: str) -> models.PersonPhoto:
        new_photo = models.PersonPhoto(
            user_id=user_id,
            filename_original=filename_original,
            filename=filename,
            uploaded_at=datetime.utcnow(),
        )
        self.db.add(new_photo)
        self.db.commit()
        self.db.refresh(new_photo)
        return new_photo

    def create_cloth_photo(self, user_id: int, filename_original: str, filename: str, fitting_type: str) -> models.ClothPhoto:
        new_cloth = models.ClothPhoto(
            user_id=user_id,
            filename_original=filename_original,
            filename=filename,
            fitting_type=fitting_type,
            uploaded_at=datetime.utcnow(),
        )
        self.db.add(new_cloth)
        self.db.commit()
        self.db.refresh(new_cloth)
        return new_cloth

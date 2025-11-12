from sqlalchemy.orm import Session
from app import models

class PhotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_person_photo_by_id(self, photo_id: int, user_id: int) -> models.PersonPhoto | None:
        return self.db.query(models.PersonPhoto).filter(
            models.PersonPhoto.id == photo_id,
            models.PersonPhoto.user_id == user_id
        ).first()

    def get_cloth_photo_by_id(self, photo_id: int) -> models.ClothPhoto | None:
        return self.db.query(models.ClothPhoto).filter(
            models.ClothPhoto.id == photo_id,
            # models.ClothPhoto.user_id == user_id
        ).first()

    def get_all_by_user_id(self, user_id: int) -> list[models.PersonPhoto]:
        return self.db.query(models.PersonPhoto).filter(
            models.PersonPhoto.user_id == user_id
        ).all()
    
    def get_all_cloth_photos_by_user_id(self, user_id: int) -> list[models.ClothPhoto]:
        return (self.db.query(models.ClothPhoto).filter(
            models.ClothPhoto.user_id == user_id
        ).order_by(models.ClothPhoto.fitting_type.desc()).all())

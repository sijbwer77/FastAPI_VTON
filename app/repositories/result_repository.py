from sqlalchemy.orm import Session
from app import models
from typing import List

class ResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_result(self, user_id: int, person_photo_id: int, cloth_photo_id: int, filename: str) -> models.ResultPhoto:
        new_result = models.ResultPhoto(
            user_id=user_id,
            person_photo_id=person_photo_id,
            cloth_photo_id=cloth_photo_id,
            filename=filename,
        )
        self.db.add(new_result)
        self.db.commit()
        self.db.refresh(new_result)
        return new_result

    def get_results_by_user_id(self, user_id: int) -> List[models.ResultPhoto]:
        return (
            self.db.query(models.ResultPhoto)
            .filter(models.ResultPhoto.user_id == user_id)
            .order_by(models.ResultPhoto.created_at.desc())
            .all()
        )

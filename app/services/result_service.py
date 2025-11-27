from typing import List, Dict, Any
from app.repositories.result_repository import ResultRepository
from app.repositories.image_repository import ImageRepository
from app import models, schemas

class ResultService:
    def __init__(self, result_repo: ResultRepository, image_repo: ImageRepository):
        self.result_repo = result_repo
        self.image_repo = image_repo

    def get_user_results(self, user_id: int) -> List[Dict[str, Any]]:
        results = self.result_repo.get_results_by_user_id(user_id)
        output = []
        for result in results:
            url = self.image_repo.get_public_url("result_photo", result.filename)
            output.append({
                "id": result.id,
                "filename": result.filename,
                "person_photo_id": result.person_photo_id,
                "cloth_photo_id": result.cloth_photo_id,
                "created_at": result.created_at,
                "image_url": url,
            })
        return output

from typing import List
from app.repositories.result_repository import ResultRepository
from app import models, schemas # For type hinting the return value

class ResultService:
    def __init__(self, result_repo: ResultRepository):
        self.result_repo = result_repo

    def get_user_results(self, user_id: int) -> List[schemas.Photo]:
        return self.result_repo.get_results_by_user_id(user_id)

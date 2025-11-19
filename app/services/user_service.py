# app/services/user_service.py
from fastapi import Depends
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app import models, schemas
from app.database import get_db

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_user_by_id(self, user_id: int) -> models.User | None:
        return self.user_repo.get_by_id(user_id)

# 의존성 주입을 위한 함수
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

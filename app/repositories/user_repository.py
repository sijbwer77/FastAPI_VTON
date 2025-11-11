from sqlalchemy.orm import Session
from app import models, schemas
from typing import List

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> models.User | None:
        return self.db.query(models.User).filter(models.User.id == user_id).first()

    def get_by_email(self, email: str) -> models.User | None:
        return self.db.query(models.User).filter(models.User.email == email).first()

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[models.User]:
        """
        모든 사용자 목록을 가져옵니다. 페이지네이션을 지원합니다.
        """
        return self.db.query(models.User).offset(skip).limit(limit).all()

    def create_or_update_google_user(self, *, google_id: str, email: str, name: str, profile_image: str) -> models.User:
        user = self.get_by_email(email=email)
        if user:
            # Update existing user if they sign in with Google
            user.google_id = google_id
            user.name = name
            user.profile_image = profile_image
        else:
            # Create a new user
            user = models.User(
                google_id=google_id,
                email=email,
                name=name,
                profile_image=profile_image,
                is_active=True
            )
            self.db.add(user)
        
        self.db.commit()
        self.db.refresh(user)
        return user

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """
        ID로 사용자를 삭제합니다.
        """
        user = self.get_by_id(user_id=user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True


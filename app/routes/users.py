from fastapi import APIRouter, Depends
from app import models, schemas
from app.utils.security import get_current_user
from app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    # Although current_user is already fetched, we call the service
    # to maintain a consistent architectural pattern.
    # The service could add more business logic here in the future.
    return user_service.get_user_by_id(current_user.id)

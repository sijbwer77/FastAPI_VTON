from fastapi import Depends, HTTPException, status
from app import models
from app.utils.security import get_current_user

def get_admin_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    """
    현재 사용자가 슈퍼유저인지 확인합니다.
    슈퍼유저가 아닐 경우, 403 Forbidden 에러를 발생시킵니다.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user

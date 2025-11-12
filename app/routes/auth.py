from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app import schemas

router = APIRouter(prefix="/auth", tags=["auth"])

# Dependency for AuthService
def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Admin login endpoint. Delegates to AuthService to authenticate and get JWT token.
    """
    return auth_service.admin_login(form_data)


@router.get('/google/login')
async def login_via_google(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.handle_google_login(request)


@router.get('/google/callback', name='auth_via_google')
async def auth_via_google(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        _, redirect_url = await auth_service.handle_google_callback(request)
        return RedirectResponse(url=redirect_url)
    except HTTPException as e:
        # Redirect with error if authentication fails
        return RedirectResponse(url=f"/?error={e.detail}")

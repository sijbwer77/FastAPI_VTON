# app/services/auth_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from datetime import timedelta

from app.config import settings
from app.repositories.user_repository import UserRepository
from app.utils.security import create_access_token
from app import schemas

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.oauth = self._configure_oauth()

    def _configure_oauth(self):
        oauth = OAuth()
        oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'}
        )
        return oauth

    def admin_login(self, form_data: OAuth2PasswordRequestForm) -> schemas.Token:
        """
        Admin login logic.
        """
        if not (form_data.username == settings.ADMIN_USERNAME and form_data.password == settings.ADMIN_PASSWORD):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = self.user_repo.get_by_email(email=form_data.username)
        if not user or not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or not an admin",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        return schemas.Token(access_token=access_token, token_type="bearer")

    async def handle_google_login(self, request: Request):
        redirect_uri = request.url_for('auth_via_google')
        return await self.oauth.google.authorize_redirect(request, redirect_uri)

    async def handle_google_callback(self, request: Request) -> tuple[str, str]:
        """
        Handles Google callback, creates/updates user, and returns access token and redirect URL.
        """
        try:
            token = await self.oauth.google.authorize_access_token(request)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authentication failed")

        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User info missing")

        user = self.user_repo.create_or_update_google_user(
            google_id=user_info['sub'],
            email=user_info['email'],
            name=user_info['name'],
            profile_image=user_info['picture']
        )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        redirect_url = f"/#token={access_token}"
        return access_token, redirect_url

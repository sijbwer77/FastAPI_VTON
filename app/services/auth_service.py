# app/services/auth_service.py
import base64
import json
import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from datetime import timedelta
from typing import Optional

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

    def _encode_state(self, data: dict) -> str:
        json_str = json.dumps(data)
        return base64.urlsafe_b64encode(json_str.encode()).decode()

    def _decode_state(self, state_str: str) -> dict:
        try:
            return json.loads(base64.urlsafe_b64decode(state_str.encode()).decode())
        except Exception:
            return {}

    async def handle_google_login(self, request: Request, redirect_uri: Optional[str] = None):
        nonce = secrets.token_urlsafe(16)
        
        state_data = {
            "nonce": nonce,
            "redirect_uri": redirect_uri or "/"
        }
        state = self._encode_state(state_data)
        
        callback_uri = request.url_for('auth_via_google')
        return await self.oauth.google.authorize_redirect(request, callback_uri, state=state)

    async def handle_google_callback(self, request: Request) -> tuple[str, str]:
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
        
        state_str = request.query_params.get('state')
        target_url = "/"
        if state_str:
             state_data = self._decode_state(state_str)
             target_url = state_data.get('redirect_uri', '/')

        redirect_url = f"{target_url}#token={access_token}"
        
        return access_token, redirect_url

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config import settings
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Configure Authlib's OAuth client
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get('/google/login')
async def login_via_google(request: Request):
    # The redirect_uri must match the one configured in Google Cloud Console
    redirect_uri = request.url_for('auth_via_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/callback', name='auth_via_google')
async def auth_via_google(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        return RedirectResponse(url="/?error=auth_failed")

    user_info = token.get('userinfo')
    if not user_info:
        return RedirectResponse(url="/?error=userinfo_missing")

    # Create or update user in the database
    user_repo = UserRepository(db)
    user = user_repo.create_or_update_google_user(
        google_id=user_info['sub'],
        email=user_info['email'],
        name=user_info['name'],
        profile_image=user_info['picture']
    )

    # Create our own access token (JWT)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Redirect to the frontend with the token
    # The frontend will grab the token from the URL hash
    response = RedirectResponse(url=f"/#token={access_token}")
    return response

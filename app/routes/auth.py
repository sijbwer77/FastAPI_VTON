from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config import settings
from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.utils.security import create_access_token # security -> utils 로 변경된 경로 반영

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

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Admin login endpoint. Authenticates against settings and DB, returns JWT token.
    """
    user_repo = UserRepository(db)
    # 1. Check credentials against settings
    if not (form_data.username == settings.ADMIN_USERNAME and form_data.password == settings.ADMIN_PASSWORD):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Check if user exists in DB and is a superuser
    user = user_repo.get_by_email(email=form_data.username)
    if not user or not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or not an admin",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create and return access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


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

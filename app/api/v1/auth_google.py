# app/api/v1/auth_google.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.schemas.user import Token, UserResponse
from app.models.user import OAuthProvider

router = APIRouter(prefix="/auth/google", tags=["OAuth"])

# Initialize OAuth
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


@router.get("/login")
async def google_login(request: Request):
    """Redirect to Google OAuth login [file:21]"""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback [file:21]"""
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        # Extract user data
        email = user_info.get('email')
        google_id = user_info.get('sub')
        full_name = user_info.get('name')
        
        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or Google ID not found"
            )
        
        # Get or create user
        user = AuthService.get_or_create_oauth_user(
            db=db,
            email=email,
            oauth_provider=OAuthProvider.GOOGLE.value,
            oauth_id=google_id,
            full_name=full_name
        )
        
        # Create tokens
        tokens = AuthService.create_tokens(user.id)
        
        # Redirect to frontend with token
        frontend_url = settings.CORS_ORIGINS[0]
        redirect_url = f"{frontend_url}/auth/callback?token={tokens['access_token']}&refresh_token={tokens['refresh_token']}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.get("/user-info")
async def get_google_user_info(request: Request):
    """Get user info from Google (for testing)"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        return user_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

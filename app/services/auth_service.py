# app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegister
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service [file:21]"""
    
    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """Register new user [file:21]"""
        
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise ValueError("User with this email or username already exists")
        
        # Create new user
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.username}")
        return new_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password [file:21]"""
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not user.password_hash:
            # OAuth user trying to login with password
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_tokens(user_id: int) -> Dict[str, str]:
        """Create access and refresh tokens [file:21]"""
        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id)
        }
    
    @staticmethod
    def get_or_create_oauth_user(
        db: Session,
        email: str,
        oauth_provider: str,
        oauth_id: str,
        full_name: Optional[str] = None
    ) -> User:
        """Get or create user from OAuth login [file:21]"""
        
        # Try to find existing OAuth user
        user = db.query(User).filter(
            User.oauth_provider == oauth_provider,
            User.oauth_id == oauth_id
        ).first()
        
        if user:
            user.last_login = datetime.utcnow()
            db.commit()
            return user
        
        # Try to find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if user:
            # Link OAuth account to existing user
            user.oauth_provider = oauth_provider
            user.oauth_id = oauth_id
            user.last_login = datetime.utcnow()
            db.commit()
            return user
        
        # Create new OAuth user
        username = email.split('@')[0]
        base_username = username
        counter = 1
        
        # Ensure unique username
        while db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            is_active=True,
            last_login=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New OAuth user created: {new_user.username}")
        return new_user

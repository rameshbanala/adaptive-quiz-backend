# app/utils/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings
from typing import Optional
import hashlib


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prepare_password(password: str) -> bytes:
    """
    Prepare password for bcrypt hashing.
    Bcrypt has a 72-byte limit, so we hash long passwords with SHA256 first.
    """
    # Convert to bytes
    password_bytes = password.encode('utf-8')
    
    # If password is longer than 72 bytes, hash it first with SHA256
    if len(password_bytes) > 72:
        return hashlib.sha256(password_bytes).hexdigest().encode('utf-8')
    
    return password_bytes


def hash_password(password: str) -> str:
    """Hash a password [file:21]"""
    prepared = _prepare_password(password)
    return pwd_context.hash(prepared)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash [file:21]"""
    prepared = _prepare_password(plain_password)
    return pwd_context.verify(prepared, hashed_password)


def create_access_token(user_id: int) -> str:
    """Create JWT access token [file:21]"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    """Create JWT refresh token [file:21]"""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token [file:21]"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

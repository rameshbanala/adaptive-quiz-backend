# app/api/v1/__init__.py
# Remove duplicate imports - keep it simple
from app.api.v1 import auth, content, quiz, analytics

__all__ = ["auth", "content", "quiz", "analytics"]

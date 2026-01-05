# app/models/content.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ContentType(str, enum.Enum):
    """Content source types [file:21]"""
    PDF = "pdf"
    URL = "url"
    TEXT = "text"


class Content(Base):
    """Content model for uploaded materials [file:21]"""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Content info
    content_type = Column(Enum(ContentType), nullable=False)
    title = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    processed_text = Column(Text, nullable=True)
    
    # CHANGED: metadata -> content_metadata
    content_metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="content")
    questions = relationship("Question", back_populates="content", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="content")
    
    def __repr__(self):
        return f"<Content {self.title}>"

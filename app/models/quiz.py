# app/models/quiz.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class QuizStatus(str, enum.Enum):
    """Quiz status [file:21]"""
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class Quiz(Base):
    """Quiz session model [file:21]"""
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="SET NULL"), nullable=True)
    
    # Quiz configuration
    topic = Column(String(100), nullable=True)
    total_questions = Column(Integer, nullable=False)
    initial_difficulty = Column(String(20), nullable=False)
    
    # Results
    status = Column(Enum(QuizStatus), default=QuizStatus.IN_PROGRESS)
    score = Column(Float, nullable=True)
    correct_answers = Column(Integer, default=0)
    total_time_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    content = relationship("Content", back_populates="quizzes")
    responses = relationship("UserResponse", back_populates="quiz", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Quiz {self.id} - {self.status}>"

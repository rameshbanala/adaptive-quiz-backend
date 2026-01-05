# app/models/question.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class QuestionType(str, enum.Enum):
    """Question types [file:21]"""
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"


class Difficulty(str, enum.Enum):
    """Question difficulty levels [file:21]"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(Base):
    """Question model [file:21]"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=False)
    
    # Question details
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    options = Column(JSONB, nullable=True)  # For MCQ: ["opt1", "opt2", "opt3", "opt4"]
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    # Classification
    difficulty = Column(Enum(Difficulty), nullable=False, index=True)
    topic = Column(String(100), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    content = relationship("Content", back_populates="questions")
    responses = relationship("UserResponse", back_populates="question")
    
    def __repr__(self):
        return f"<Question {self.id} - {self.difficulty}>"

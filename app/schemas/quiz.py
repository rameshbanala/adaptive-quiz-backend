# app/schemas/quiz.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.question import QuestionType, Difficulty
from app.models.quiz import QuizStatus


# Quiz Generation Request [file:21]
class QuizGenerateRequest(BaseModel):
    content_id: int
    num_questions: int = Field(10, ge=5, le=50)
    difficulty: Difficulty = Difficulty.MEDIUM
    question_types: List[QuestionType] = [QuestionType.MCQ, QuestionType.TRUE_FALSE]


# Question Response
class QuestionResponse(BaseModel):
    id: int
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]]
    difficulty: Difficulty
    topic: Optional[str]
    
    class Config:
        from_attributes = True


# Quiz Response
class QuizResponse(BaseModel):
    id: int
    user_id: int
    content_id: Optional[int]
    topic: Optional[str]
    total_questions: int
    status: QuizStatus
    score: Optional[float]
    correct_answers: int
    started_at: datetime
    completed_at: Optional[datetime]
    questions: List[QuestionResponse]
    
    class Config:
        from_attributes = True


# Answer Submission [file:21]
class AnswerSubmit(BaseModel):
    question_id: int
    user_answer: str
    time_taken_seconds: Optional[int] = None


# Answer Result
class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]
    next_difficulty: Optional[Difficulty]


# Quiz Results [file:21]
class QuizResults(BaseModel):
    quiz_id: int
    score: float
    correct_answers: int
    total_questions: int
    total_time_seconds: Optional[int]
    accuracy: float
    difficulty_progression: List[str]
    
    class Config:
        from_attributes = True

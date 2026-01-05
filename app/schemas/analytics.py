# app/schemas/analytics.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime


# Topic Performance
class TopicPerformance(BaseModel):
    topic: str
    total_questions: int
    correct_answers: int
    accuracy: float
    avg_time_per_question: float


# User Analytics Overview [file:21]
class AnalyticsOverview(BaseModel):
    total_quizzes: int
    total_questions_answered: int
    overall_accuracy: float
    avg_score: float
    current_skill_level: str
    topics_mastered: List[str]
    topics_to_improve: List[str]
    performance_by_topic: List[TopicPerformance]


# Progress Chart Data [file:21]
class ProgressChartData(BaseModel):
    date: datetime
    accuracy: float
    questions_answered: int


# Analytics Response
class AnalyticsResponse(BaseModel):
    overview: AnalyticsOverview
    progress_chart: List[ProgressChartData]
    recent_quizzes: List[Dict]

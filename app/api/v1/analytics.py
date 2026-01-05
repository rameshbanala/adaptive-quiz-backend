# app/api/v1/analytics.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.schemas.analytics import AnalyticsOverview, AnalyticsResponse, TopicPerformance, ProgressChartData
from app.models.user import User
from app.models.quiz import Quiz, QuizStatus
from app.models.response import UserResponse
from app.models.analytics import UserAnalytics
from app.utils.dependencies import get_current_user
from app.services.cache_service import CacheService
from typing import List
import logging

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)


@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user analytics overview [file:21]"""
    
    # Check cache first [web:4]
    cached = await CacheService.get_cached_analytics(current_user.id)
    if cached:
        logger.info(f"Analytics cache hit for user {current_user.id}")
        return AnalyticsResponse(**cached)
    
    # Get completed quizzes
    completed_quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id,
        Quiz.status == QuizStatus.COMPLETED
    ).all()
    
    total_quizzes = len(completed_quizzes)
    
    if total_quizzes == 0:
        return AnalyticsResponse(
            overview=AnalyticsOverview(
                total_quizzes=0,
                total_questions_answered=0,
                overall_accuracy=0.0,
                avg_score=0.0,
                current_skill_level=current_user.skill_level.value,
                topics_mastered=[],
                topics_to_improve=[],
                performance_by_topic=[]
            ),
            progress_chart=[],
            recent_quizzes=[]
        )
    
    # Calculate overall stats
    total_questions = sum(q.total_questions for q in completed_quizzes)
    total_correct = sum(q.correct_answers for q in completed_quizzes)
    overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
    avg_score = sum(q.score for q in completed_quizzes if q.score) / total_quizzes
    
    # Get topic performance
    topic_stats = db.query(
        Quiz.topic,
        func.count(Quiz.id).label('quiz_count'),
        func.sum(Quiz.correct_answers).label('correct'),
        func.sum(Quiz.total_questions).label('total')
    ).filter(
        Quiz.user_id == current_user.id,
        Quiz.status == QuizStatus.COMPLETED
    ).group_by(Quiz.topic).all()
    
    performance_by_topic = []
    topics_mastered = []
    topics_to_improve = []
    
    for stat in topic_stats:
        if stat.total and stat.total > 0:
            accuracy = (stat.correct / stat.total) * 100
            performance_by_topic.append(
                TopicPerformance(
                    topic=stat.topic or "General",
                    total_questions=stat.total,
                    correct_answers=stat.correct,
                    accuracy=round(accuracy, 2),
                    avg_time_per_question=0.0  # Can calculate if needed
                )
            )
            
            if accuracy >= 80:
                topics_mastered.append(stat.topic or "General")
            elif accuracy < 60:
                topics_to_improve.append(stat.topic or "General")
    
    # Progress chart data
    progress_data = []
    for quiz in completed_quizzes[-10:]:  # Last 10 quizzes
        if quiz.total_questions > 0:
            accuracy = (quiz.correct_answers / quiz.total_questions) * 100
            progress_data.append(
                ProgressChartData(
                    date=quiz.completed_at,
                    accuracy=round(accuracy, 2),
                    questions_answered=quiz.total_questions
                )
            )
    
    # Recent quizzes
    recent_quizzes = [
        {
            "id": q.id,
            "topic": q.topic,
            "score": q.score,
            "completed_at": q.completed_at.isoformat()
        }
        for q in completed_quizzes[-5:]
    ]
    
    response = AnalyticsResponse(
        overview=AnalyticsOverview(
            total_quizzes=total_quizzes,
            total_questions_answered=total_questions,
            overall_accuracy=round(overall_accuracy, 2),
            avg_score=round(avg_score, 2),
            current_skill_level=current_user.skill_level.value,
            topics_mastered=topics_mastered,
            topics_to_improve=topics_to_improve,
            performance_by_topic=performance_by_topic
        ),
        progress_chart=progress_data,
        recent_quizzes=recent_quizzes
    )
    
    # Cache analytics [web:4]
    await CacheService.cache_user_analytics(current_user.id, response.model_dump())
    
    logger.info(f"Analytics calculated for user {current_user.id}")
    return response

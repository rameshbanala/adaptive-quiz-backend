# app/api/v1/quiz.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.quiz import (
    QuizGenerateRequest, QuizResponse, QuestionResponse,
    AnswerSubmit, AnswerResult, QuizResults
)
from app.models.user import User
from app.models.content import Content
from app.models.question import Question, QuestionType, Difficulty
from app.models.quiz import Quiz, QuizStatus
from app.models.response import UserResponse
from app.utils.dependencies import get_current_user
from app.services.groq_service import GroqQuestionGenerator
from app.services.adaptive_engine import AdaptiveDifficultyEngine
from app.services.cache_service import CacheService
from app.services.content_parser import ContentParserService
from datetime import datetime
import logging

router = APIRouter(prefix="/quiz", tags=["Quiz Management"])
logger = logging.getLogger(__name__)

groq_generator = GroqQuestionGenerator()
adaptive_engine = AdaptiveDifficultyEngine()


@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate new quiz from content [file:21]"""
    
    # Validate content exists and belongs to user
    content = db.query(Content).filter(
        Content.id == request.content_id,
        Content.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check cache first [web:4]
    cached_questions = await CacheService.get_cached_questions(
        content.id,
        request.difficulty.value
    )
    
    if cached_questions:
        questions = cached_questions[:request.num_questions]
        logger.info(f"Using {len(questions)} cached questions")
    else:
        # Generate questions using Groq [web:1]
        question_types = [qt.value for qt in request.question_types]
        
        generated = await groq_generator.generate_questions(
            content=content.raw_text[:4000],  # Limit content length
            num_questions=request.num_questions,
            difficulty=request.difficulty.value,
            question_types=question_types
        )
        
        if not generated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate questions"
            )
        
        # Save questions to database
        questions = []
        for q_data in generated:
            question = Question(
                content_id=content.id,
                question_text=q_data["question"],
                question_type=QuestionType(q_data["type"]),
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation"),
                difficulty=Difficulty(q_data["difficulty"]),
                topic=q_data.get("topic")
            )
            db.add(question)
            questions.append(question)
        
        db.commit()
        
        # Cache questions [web:4]
        await CacheService.cache_generated_questions(
            content.id,
            request.difficulty.value,
            [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type.value,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "difficulty": q.difficulty.value,
                    "topic": q.topic
                }
                for q in questions
            ]
        )
    
    # Create quiz session
    quiz = Quiz(
        user_id=current_user.id,
        content_id=content.id,
        topic=content.title,
        total_questions=len(questions),
        initial_difficulty=request.difficulty.value
    )
    
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Prepare response
    question_responses = []
    for q in questions:
        if isinstance(q, dict):
            question_responses.append(QuestionResponse(**q))
        else:
            question_responses.append(QuestionResponse.model_validate(q))
    
    logger.info(f"Quiz created: {quiz.id} with {len(questions)} questions")
    
    return QuizResponse(
        id=quiz.id,
        user_id=quiz.user_id,
        content_id=quiz.content_id,
        topic=quiz.topic,
        total_questions=quiz.total_questions,
        status=quiz.status,
        score=quiz.score,
        correct_answers=quiz.correct_answers,
        started_at=quiz.started_at,
        completed_at=quiz.completed_at,
        questions=question_responses
    )


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quiz by ID with questions"""
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Get questions for this quiz's content
    questions = db.query(Question).filter(
        Question.content_id == quiz.content_id
    ).limit(quiz.total_questions).all()
    
    question_responses = [QuestionResponse.model_validate(q) for q in questions]
    
    return QuizResponse(
        id=quiz.id,
        user_id=quiz.user_id,
        content_id=quiz.content_id,
        topic=quiz.topic,
        total_questions=quiz.total_questions,
        status=quiz.status,
        score=quiz.score,
        correct_answers=quiz.correct_answers,
        started_at=quiz.started_at,
        completed_at=quiz.completed_at,
        questions=question_responses
    )


@router.post("/{quiz_id}/submit-answer", response_model=AnswerResult)
async def submit_answer(
    quiz_id: int,
    answer: AnswerSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit answer for a question [file:21]"""
    
    # Validate quiz
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if quiz.status == QuizStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already completed"
        )
    
    # Validate question
    question = db.query(Question).filter(Question.id == answer.question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if already answered
    existing = db.query(UserResponse).filter(
        UserResponse.quiz_id == quiz_id,
        UserResponse.question_id == answer.question_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question already answered"
        )
    
    # Check correctness
    is_correct = answer.user_answer.strip().lower() == question.correct_answer.strip().lower()
    
    # Save response
    response = UserResponse(
        quiz_id=quiz_id,
        question_id=question.id,
        user_answer=answer.user_answer,
        is_correct=is_correct,
        time_taken_seconds=answer.time_taken_seconds,
        difficulty_at_attempt=question.difficulty.value
    )
    
    db.add(response)
    
    # Update quiz stats
    if is_correct:
        quiz.correct_answers += 1
    
    db.commit()
    
    # Calculate next difficulty [file:21]
    performance_history = adaptive_engine.get_user_performance_history(db, quiz_id)
    next_difficulty = adaptive_engine.calculate_next_difficulty(
        question.difficulty,
        performance_history
    )
    
    logger.info(f"Answer submitted: Quiz {quiz_id}, Question {question.id}, Correct: {is_correct}")
    
    return AnswerResult(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        next_difficulty=next_difficulty
    )


@router.post("/{quiz_id}/complete", response_model=QuizResults)
async def complete_quiz(
    quiz_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete quiz and get results [file:21]"""
    
    quiz = db.query(Quiz).filter(
        Quiz.id == quiz_id,
        Quiz.user_id == current_user.id
    ).first()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    if quiz.status == QuizStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already completed"
        )
    
    # Calculate final score
    results = adaptive_engine.calculate_quiz_score(db, quiz_id)
    
    # Update quiz
    quiz.status = QuizStatus.COMPLETED
    quiz.score = results["score"]
    quiz.correct_answers = results["correct_answers"]
    quiz.completed_at = datetime.utcnow()
    
    # Calculate total time
    responses = db.query(UserResponse).filter(UserResponse.quiz_id == quiz_id).all()
    total_time = sum(r.time_taken_seconds for r in responses if r.time_taken_seconds)
    quiz.total_time_seconds = total_time
    
    db.commit()
    
    # Get difficulty progression
    difficulty_progression = [r.difficulty_at_attempt for r in responses]
    
    # Invalidate analytics cache [web:4]
    background_tasks.add_task(CacheService.invalidate_user_cache, current_user.id)
    
    logger.info(f"Quiz completed: {quiz_id}, Score: {results['score']}")
    
    return QuizResults(
        quiz_id=quiz.id,
        score=results["score"],
        correct_answers=results["correct_answers"],
        total_questions=results["total_questions"],
        total_time_seconds=total_time,
        accuracy=results["accuracy"],
        difficulty_progression=difficulty_progression
    )


@router.get("/history", response_model=List[QuizResponse])
async def get_quiz_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """Get user's quiz history [file:21]"""
    
    quizzes = db.query(Quiz)\
        .filter(Quiz.user_id == current_user.id)\
        .order_by(Quiz.started_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        QuizResponse(
            id=q.id,
            user_id=q.user_id,
            content_id=q.content_id,
            topic=q.topic,
            total_questions=q.total_questions,
            status=q.status,
            score=q.score,
            correct_answers=q.correct_answers,
            started_at=q.started_at,
            completed_at=q.completed_at,
            questions=[]
        )
        for q in quizzes
    ]

# app/services/adaptive_engine.py
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.response import UserResponse
from app.models.question import Difficulty
import logging

logger = logging.getLogger(__name__)


class AdaptiveDifficultyEngine:
    """Adaptive difficulty adjustment engine [file:21]"""
    
    DIFFICULTY_LEVELS = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
    PERFORMANCE_WINDOW = 5  # Last 5 questions
    
    def __init__(self):
        self.accuracy_thresholds = {
            "increase": 0.8,  # 80% accuracy to increase difficulty
            "decrease": 0.4,  # 40% accuracy to decrease difficulty
        }
    
    def calculate_next_difficulty(
        self,
        current_difficulty: Difficulty,
        recent_responses: List[bool]
    ) -> Difficulty:
        """Calculate next difficulty based on performance [file:21]"""
        
        if len(recent_responses) < 2:
            return current_difficulty
        
        # Calculate accuracy in recent window
        recent = recent_responses[-self.PERFORMANCE_WINDOW:]
        accuracy = sum(recent) / len(recent)
        
        current_idx = self.DIFFICULTY_LEVELS.index(current_difficulty)
        
        # Adjustment logic [file:21]
        if accuracy >= self.accuracy_thresholds["increase"]:
            # Increase difficulty if performing well
            new_idx = min(current_idx + 1, len(self.DIFFICULTY_LEVELS) - 1)
            logger.info(f"Increasing difficulty: {current_difficulty} -> {self.DIFFICULTY_LEVELS[new_idx]}")
        elif accuracy <= self.accuracy_thresholds["decrease"]:
            # Decrease difficulty if struggling
            new_idx = max(current_idx - 1, 0)
            logger.info(f"Decreasing difficulty: {current_difficulty} -> {self.DIFFICULTY_LEVELS[new_idx]}")
        else:
            # Maintain current difficulty
            new_idx = current_idx
        
        return self.DIFFICULTY_LEVELS[new_idx]
    
    def get_user_performance_history(
        self,
        db: Session,
        quiz_id: int,
        limit: int = 10
    ) -> List[bool]:
        """Get user's recent performance in current quiz [file:21]"""
        
        responses = db.query(UserResponse)\
            .filter(UserResponse.quiz_id == quiz_id)\
            .order_by(UserResponse.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [resp.is_correct for resp in reversed(responses)]
    
    def select_next_question(
        self,
        available_questions: List[Dict],
        target_difficulty: Difficulty,
        answered_question_ids: set
    ) -> Optional[Dict]:
        """Select next question based on difficulty [file:21]"""
        
        # Filter unanswered questions
        unanswered = [
            q for q in available_questions 
            if q["id"] not in answered_question_ids
        ]
        
        if not unanswered:
            return None
        
        # Try to find question with target difficulty
        target_questions = [
            q for q in unanswered 
            if q["difficulty"] == target_difficulty.value
        ]
        
        if target_questions:
            return target_questions[0]
        
        # Fallback: return any unanswered question
        return unanswered[0]
    
    def calculate_quiz_score(
        self,
        db: Session,
        quiz_id: int
    ) -> Dict[str, float]:
        """Calculate final quiz score and metrics [file:21]"""
        
        responses = db.query(UserResponse)\
            .filter(UserResponse.quiz_id == quiz_id)\
            .all()
        
        if not responses:
            return {
                "score": 0.0,
                "accuracy": 0.0,
                "correct_answers": 0,
                "total_questions": 0
            }
        
        correct = sum(1 for r in responses if r.is_correct)
        total = len(responses)
        accuracy = (correct / total) * 100
        
        # Score calculation (can be weighted by difficulty)
        score = accuracy
        
        return {
            "score": round(score, 2),
            "accuracy": round(accuracy, 2),
            "correct_answers": correct,
            "total_questions": total
        }

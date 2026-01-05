# app/services/groq_service.py
from groq import Groq
import json
from typing import List, Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GroqQuestionGenerator:
    """Groq API service for question generation [file:21][web:1]"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    async def generate_questions(
        self,
        content: str,
        num_questions: int = 10,
        difficulty: str = "medium",
        question_types: List[str] = ["mcq", "true_false"]
    ) -> List[Dict]:
        """Generate questions using Groq API [file:21]"""
        
        # Create prompt
        prompt = self._create_prompt(content, num_questions, difficulty, question_types)
        
        try:
            # Call Groq API [web:1]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational content creator. Generate high-quality quiz questions that test understanding, not just memorization."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            questions = result.get("questions", [])
            
            # Validate and clean questions
            validated_questions = self._validate_questions(questions, question_types)
            
            logger.info(f"Generated {len(validated_questions)} questions")
            return validated_questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return []
    
    def _create_prompt(
        self,
        content: str,
        num_questions: int,
        difficulty: str,
        question_types: List[str]
    ) -> str:
        """Create prompt for Groq API [file:21]"""
        
        # Truncate content if too long
        max_content_length = 4000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""Generate {num_questions} educational quiz questions from the following content.

CONTENT:
{content}

REQUIREMENTS:
- Difficulty level: {difficulty} (easy/medium/hard)
- Question types: {', '.join(question_types)}
- For MCQ: Provide exactly 4 options with only 1 correct answer
- For True/False: Provide clear true or false statements
- Include brief explanation for each answer
- Extract relevant topic for each question
- Ensure questions test comprehension, not just memorization

OUTPUT FORMAT (JSON):
{{
  "questions": [
    {{
      "question": "What is the main concept discussed?",
      "type": "mcq",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option B",
      "explanation": "Brief explanation here",
      "difficulty": "{difficulty}",
      "topic": "Main Topic"
    }},
    {{
      "question": "The text states that X is true.",
      "type": "true_false",
      "options": ["True", "False"],
      "correct_answer": "True",
      "explanation": "Brief explanation",
      "difficulty": "{difficulty}",
      "topic": "Sub Topic"
    }}
  ]
}}

Generate diverse, high-quality questions now."""
        
        return prompt
    
    def _validate_questions(
        self,
        questions: List[Dict],
        expected_types: List[str]
    ) -> List[Dict]:
        """Validate and clean generated questions [file:21]"""
        
        validated = []
        
        for q in questions:
            # Check required fields
            if not all(k in q for k in ["question", "type", "correct_answer"]):
                continue
            
            # Validate question type
            if q["type"] not in expected_types:
                continue
            
            # Validate MCQ has 4 options
            if q["type"] == "mcq":
                if "options" not in q or len(q.get("options", [])) != 4:
                    continue
            
            # Validate True/False has 2 options
            if q["type"] == "true_false":
                q["options"] = ["True", "False"]
            
            # Ensure all fields exist
            q.setdefault("explanation", "")
            q.setdefault("difficulty", "medium")
            q.setdefault("topic", "General")
            
            validated.append(q)
        
        return validated

# init_db.py
"""
Database initialization script for NeonDB
Run this script to create all tables
"""

import sys
import asyncio
from app.core.database import Base, engine
from app.core.config import settings

# Import all models
from app.models.user import User
from app.models.content import Content
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.response import UserResponse
from app.models.analytics import UserAnalytics


def create_tables():
    """Create all database tables"""
    print("=" * 60)
    print("Smart Quizzer - Database Initialization")
    print("=" * 60)
    print(f"\nDatabase: NeonDB")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"\nConnection: {settings.DATABASE_URL[:50]}...")
    print("\n" + "=" * 60)
    
    try:
        print("\n📋 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")
        
        print("\n✓ Tables created:")
        print("  - users")
        print("  - content")
        print("  - questions")
        print("  - quizzes")
        print("  - user_responses")
        print("  - user_analytics")
        
        print("\n✓ ENUM types created:")
        print("  - SkillLevel (beginner, intermediate, advanced)")
        print("  - OAuthProvider (google, github)")
        print("  - ContentType (pdf, url, text)")
        print("  - QuestionType (mcq, true_false, short_answer)")
        print("  - Difficulty (easy, medium, hard)")
        print("  - QuizStatus (in_progress, completed, abandoned)")
        
        print("\n" + "=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error creating tables: {e}")
        print("\nTroubleshooting:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Verify NeonDB connection string is correct")
        print("3. Ensure your IP is not blocked by NeonDB")
        return False


def drop_tables():
    """Drop all database tables (use with caution!)"""
    print("\n⚠ WARNING: This will delete all tables and data!")
    confirm = input("Type 'DELETE ALL' to confirm: ")
    
    if confirm == "DELETE ALL":
        try:
            Base.metadata.drop_all(bind=engine)
            print("✓ All tables dropped")
            return True
        except Exception as e:
            print(f"✗ Error dropping tables: {e}")
            return False
    else:
        print("✗ Cancelled")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management")
    parser.add_argument(
        "action",
        choices=["create", "drop", "recreate"],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    if args.action == "create":
        create_tables()
    
    elif args.action == "drop":
        drop_tables()
    
    elif args.action == "recreate":
        if drop_tables():
            create_tables()

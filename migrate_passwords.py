"""
Migration script to rehash existing user passwords with the new method.

This script is needed because we changed the password hashing method to handle
bcrypt's 72-byte limit. Existing passwords in the database were hashed differently.

IMPORTANT: This script will invalidate all existing passwords. Users will need to:
1. Use the password reset feature, OR
2. Re-register if they haven't verified their email

For development/testing, you can manually update test user passwords.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User
from app.utils.security import hash_password
import sys


def migrate_passwords():
    """
    This function would rehash passwords, but since we can't retrieve plain passwords,
    we'll need to either:
    1. Reset all passwords (force password reset)
    2. Keep old hashes and handle both old and new format (complex)
    3. Manually update test users
    
    For now, this is a placeholder. In production, you'd send password reset emails.
    """
    print("Password migration required!")
    print("Options:")
    print("1. Force all users to reset their passwords")
    print("2. Manually update test user passwords in the database")
    print("3. Delete and recreate test users")
    

def create_test_user():
    """Create a test user with the new password hashing"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == "ramesh@gmail.com").first()
        
        if existing_user:
            # Update password with new hashing method
            existing_user.password_hash = hash_password("your_password_here")
            db.commit()
            print("✓ Updated existing user password")
        else:
            # Create new user
            new_user = User(
                username="Ramesh",
                email="ramesh@gmail.com",
                password_hash=hash_password("your_password_here"),
                full_name="Ramesh",
                skill_level="intermediate",
                is_active=True
            )
            db.add(new_user)
            db.commit()
            print("✓ Created new test user")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Password Migration Script")
    print("=" * 60)
    migrate_passwords()

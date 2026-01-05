# app/api/v1/content.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.content import (
    ContentUploadPDF, ContentUploadURL, ContentUploadText,
    ContentResponse, ContentListResponse
)
from app.models.user import User
from app.models.content import Content, ContentType
from app.utils.dependencies import get_current_user
from app.services.content_parser import ContentParserService
from app.core.config import settings
import logging

router = APIRouter(prefix="/content", tags=["Content Management"])
logger = logging.getLogger(__name__)


@router.post("/upload/pdf", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload PDF file [file:21]"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Check file size
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
        )
    
    try:
        # Parse PDF
        parsed_data = await ContentParserService.parse_pdf(file_content, file.filename)
        
        # Create content record
        content = Content(
            user_id=current_user.id,
            content_type=ContentType.PDF,
            title=title or file.filename,
            raw_text=parsed_data["raw_text"],
            content_metadata={  # CHANGED: metadata -> content_metadata
                "filename": parsed_data["filename"],
                "word_count": parsed_data["word_count"],
                "page_count": parsed_data.get("page_count", 0)
            }
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        logger.info(f"PDF uploaded: {content.id} by user {current_user.id}")
        return ContentResponse.model_validate(content)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/upload/url", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def upload_url(
    data: ContentUploadURL,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch content from URL [file:21]"""
    
    try:
        # Parse URL
        parsed_data = await ContentParserService.parse_url(str(data.url))
        
        # Create content record
        content = Content(
            user_id=current_user.id,
            content_type=ContentType.URL,
            title=data.title,
            raw_text=parsed_data["raw_text"],
            content_metadata={  # CHANGED: metadata -> content_metadata
                "url": parsed_data["url"],
                "word_count": parsed_data["word_count"],
                "original_title": parsed_data.get("title", "")
            }
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        logger.info(f"URL content uploaded: {content.id} by user {current_user.id}")
        return ContentResponse.model_validate(content)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/upload/text", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def upload_text(
    data: ContentUploadText,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload raw text [file:21]"""
    
    try:
        # Parse text
        parsed_data = await ContentParserService.parse_text(data.text)
        
        # Create content record
        content = Content(
            user_id=current_user.id,
            content_type=ContentType.TEXT,
            title=data.title,
            raw_text=parsed_data["raw_text"],
            content_metadata={  # CHANGED: metadata -> content_metadata
                "word_count": parsed_data["word_count"]
            }
        )
        
        db.add(content)
        db.commit()
        db.refresh(content)
        
        logger.info(f"Text content uploaded: {content.id} by user {current_user.id}")
        return ContentResponse.model_validate(content)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ContentListResponse])
async def get_user_content(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """Get user's uploaded content [file:21]"""
    
    content_list = db.query(Content)\
        .filter(Content.user_id == current_user.id)\
        .order_by(Content.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        ContentListResponse(
            id=c.id,
            content_type=c.content_type,
            title=c.title,
            created_at=c.created_at,
            word_count=c.content_metadata.get("word_count") if c.content_metadata else None  # CHANGED
        )
        for c in content_list
    ]


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific content by ID [file:21]"""
    
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return ContentResponse.model_validate(content)


@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete content [file:21]"""
    
    content = db.query(Content).filter(
        Content.id == content_id,
        Content.user_id == current_user.id
    ).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    db.delete(content)
    db.commit()
    
    logger.info(f"Content deleted: {content_id} by user {current_user.id}")

# app/schemas/content.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.content import ContentType


# Content Upload - PDF [file:21]
class ContentUploadPDF(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


# Content Upload - URL [file:21]
class ContentUploadURL(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl


# Content Upload - Text [file:21]
class ContentUploadText(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    text: str = Field(..., min_length=50)


# Content Response
class ContentResponse(BaseModel):
    id: int
    user_id: int
    content_type: ContentType
    title: str
    raw_text: str
    content_metadata: Optional[Dict[str, Any]]  # CHANGED: metadata -> content_metadata
    created_at: datetime
    
    class Config:
        from_attributes = True


# Content List Response
class ContentListResponse(BaseModel):
    id: int
    content_type: ContentType
    title: str
    created_at: datetime
    word_count: Optional[int]
    
    class Config:
        from_attributes = True

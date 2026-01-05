# app/services/content_parser.py
import PyPDF2
import pdfplumber
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import logging
import io

logger = logging.getLogger(__name__)


class ContentParserService:
    """Service for parsing content from different sources [file:21]"""
    
    @staticmethod
    async def parse_pdf(file_content: bytes, filename: str) -> Dict[str, str]:
        """Parse PDF file and extract text [file:21]"""
        try:
            # Try pdfplumber first (better for complex PDFs)
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
                
                if text.strip():
                    return {
                        "raw_text": text.strip(),
                        "word_count": len(text.split()),
                        "page_count": len(pdf.pages),
                        "filename": filename
                    }
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {e}")
        
        try:
            # Fallback to PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
            
            return {
                "raw_text": text.strip(),
                "word_count": len(text.split()),
                "page_count": len(pdf_reader.pages),
                "filename": filename
            }
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            raise ValueError(f"Could not parse PDF: {str(e)}")
    
    @staticmethod
    async def parse_url(url: str) -> Dict[str, str]:
        """Fetch and parse content from URL [file:21]"""
        try:
            # Fetch URL content
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text from main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
            else:
                text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)
            
            return {
                "raw_text": text,
                "word_count": len(text.split()),
                "url": url,
                "title": soup.title.string if soup.title else "Untitled"
            }
        except requests.RequestException as e:
            logger.error(f"URL fetch failed: {e}")
            raise ValueError(f"Could not fetch URL: {str(e)}")
        except Exception as e:
            logger.error(f"URL parsing failed: {e}")
            raise ValueError(f"Could not parse URL content: {str(e)}")
    
    @staticmethod
    async def parse_text(text: str) -> Dict[str, str]:
        """Process raw text input [file:21]"""
        if not text or len(text.strip()) < 50:
            raise ValueError("Text content must be at least 50 characters")
        
        return {
            "raw_text": text.strip(),
            "word_count": len(text.split())
        }
    
    @staticmethod
    def chunk_text(text: str, max_chunk_size: int = 2000) -> list[str]:
        """Split text into chunks for processing [file:21]"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > max_chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(word)
            current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

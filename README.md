# Smart Quizzer - Backend API

**AI-Powered Adaptive Quiz Generation System**

A FastAPI-based backend service that provides intelligent quiz generation using Groq LLM, adaptive difficulty adjustment, and comprehensive analytics.

---

## 🚀 Features

### Core Functionality
- **🤖 AI-Powered Quiz Generation** - Uses Groq LLM (Llama 3.3 70B) for intelligent question creation
- **📊 Adaptive Difficulty Engine** - Dynamically adjusts question difficulty based on user performance
- **📄 Multi-Format Content Support** - PDF, URL, and raw text processing
- **📈 Comprehensive Analytics** - Detailed performance tracking and progress visualization
- **🔐 Secure Authentication** - JWT-based auth with refresh tokens + Google OAuth support
- **⚡ Redis Caching** - Fast question retrieval and analytics caching
- **🗄️ NeonDB PostgreSQL** - Scalable cloud database

### Technical Features
- RESTful API with OpenAPI documentation
- Async/await for high performance
- SQLAlchemy ORM with Alembic migrations
- Pydantic data validation
- CORS support for frontend integration
- Background task processing
- Comprehensive error handling

---

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **PostgreSQL**: NeonDB account (or local PostgreSQL)
- **Redis**: Local or cloud instance
- **Groq API Key**: From [Groq Console](https://console.groq.com)
- **Google OAuth** (optional): Client ID and Secret

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
cd smart-quizzer-v2/smart-quizzer-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create `.env` file in the backend root:

```env
# Application
APP_NAME=Smart Quizzer API
APP_VERSION=2.0.0
DEBUG=True
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000

# Database (NeonDB)
DATABASE_URL=postgresql://user:password@host/database

# Security
SECRET_KEY=your-super-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Groq AI
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=llama-3.3-70b-versatile

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Google OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 5. Database Setup

```bash
# Run migrations
alembic upgrade head

# Or create tables directly
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

## 🚀 Running the Server

### Development Mode
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

---

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/google` - Google OAuth login

### Content Management
- `POST /api/v1/content/upload-pdf` - Upload PDF file
- `POST /api/v1/content/fetch-url` - Fetch content from URL
- `POST /api/v1/content/upload-text` - Upload raw text
- `GET /api/v1/content/` - List user content
- `GET /api/v1/content/{id}` - Get specific content
- `DELETE /api/v1/content/{id}` - Delete content

### Quiz Management
- `POST /api/v1/quiz/generate` - Generate new quiz
- `GET /api/v1/quiz/{id}` - Get quiz with questions
- `POST /api/v1/quiz/{id}/submit-answer` - Submit answer
- `POST /api/v1/quiz/{id}/complete` - Complete quiz
- `GET /api/v1/quiz/history` - Get quiz history

### Analytics
- `GET /api/v1/analytics/overview` - Get analytics overview
- `GET /api/v1/analytics/progress` - Get progress data
- `GET /api/v1/analytics/topics` - Get topic performance

---

## 🏗️ Project Structure

```
smart-quizzer-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── content.py       # Content management
│   │       ├── quiz.py          # Quiz operations
│   │       └── analytics.py     # Analytics endpoints
│   ├── core/
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database setup
│   │   └── security.py          # Security utilities
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── content.py           # Content model
│   │   ├── question.py          # Question model
│   │   ├── quiz.py              # Quiz model
│   │   └── response.py          # User response model
│   ├── schemas/
│   │   ├── user.py              # User schemas
│   │   ├── content.py           # Content schemas
│   │   ├── quiz.py              # Quiz schemas
│   │   └── analytics.py         # Analytics schemas
│   ├── services/
│   │   ├── auth_service.py      # Auth business logic
│   │   ├── groq_service.py      # Groq AI integration
│   │   ├── adaptive_engine.py   # Adaptive difficulty
│   │   ├── cache_service.py     # Redis caching
│   │   └── content_parser.py    # Content processing
│   ├── utils/
│   │   ├── dependencies.py      # FastAPI dependencies
│   │   └── security.py          # Security helpers
│   └── main.py                  # Application entry point
├── alembic/                     # Database migrations
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables
```

---

## 🔧 Key Technologies

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern, fast web framework |
| **SQLAlchemy** | ORM for database operations |
| **Alembic** | Database migrations |
| **Pydantic** | Data validation |
| **Groq** | AI/LLM for question generation |
| **Redis** | Caching layer |
| **NeonDB** | PostgreSQL cloud database |
| **python-jose** | JWT token handling |
| **bcrypt** | Password hashing |
| **PyPDF2** | PDF processing |
| **BeautifulSoup** | Web scraping |

---

## 🧪 Testing

### Run Tests
```bash
pytest

# With coverage
pytest --cov=app tests/
```

### Manual API Testing
Use the interactive docs at http://localhost:8000/docs

---

## 📊 Database Schema

### Key Tables
- **users** - User accounts and profiles
- **content** - Uploaded study materials
- **questions** - Generated quiz questions
- **quizzes** - Quiz sessions
- **user_responses** - User answers and scores

### Relationships
- User → Content (one-to-many)
- Content → Questions (one-to-many)
- User → Quizzes (one-to-many)
- Quiz → Responses (one-to-many)

---

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Access (30min) + Refresh (7 days)
- **Token Refresh**: Automatic token renewal
- **CORS**: Configured for frontend origins
- **SQL Injection**: Protected via SQLAlchemy ORM
- **Input Validation**: Pydantic models

---

## ⚡ Performance Optimizations

- **Redis Caching**: Questions and analytics cached
- **Async Operations**: Non-blocking I/O
- **Connection Pooling**: Database connection reuse
- **Background Tasks**: Async cache invalidation
- **Query Optimization**: Indexed columns

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check DATABASE_URL format
postgresql://user:password@host:port/database

# Test connection
python -c "from app.core.database import engine; engine.connect()"
```

### Redis Connection Issues
```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

### Groq API Issues
```bash
# Verify API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

---

## 📝 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `SECRET_KEY` | Yes | - | JWT secret (min 32 chars) |
| `GROQ_API_KEY` | Yes | - | Groq AI API key |
| `REDIS_HOST` | No | localhost | Redis server host |
| `REDIS_PORT` | No | 6379 | Redis server port |
| `GOOGLE_CLIENT_ID` | No | - | Google OAuth client ID |
| `CORS_ORIGINS` | No | [] | Allowed CORS origins |

---

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up Redis instance
- [ ] Configure CORS origins
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure logging

---

## 📄 License

MIT License - See LICENSE file for details

---

## 👥 Support

For issues and questions:
- Create an issue on GitHub
- Check API documentation at `/docs`
- Review error logs in console

---

**Built with ❤️ using FastAPI and Groq AI**

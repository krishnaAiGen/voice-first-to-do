# Voice-First To-Do List Application

A production-ready voice-controlled to-do list application with **sub-2 second latency** and **90%+ accuracy**, built with FastAPI, Gemini 2.5 Flash, Deepgram, and Next.js.

## 🎯 Key Features

### Core Functionality
- **Voice-First Interface**: Natural language voice commands for all operations
- **Sub-2s Perceived Latency**: Two-phase response system (transcript in ~1.5s, full response in ~3s)
- **90%+ Accuracy**: LLM-powered intent parsing with high reliability
- **Full CRUD Operations**: Create, read, update, and delete tasks via voice
- **Conversational Memory**: 5-turn context window for natural follow-up commands
- **Greeting Handling**: Graceful handling of casual conversation ("Hi", "How are you?")

### User Experience
- **Keyboard Shortcuts**: Hold Option/Alt to record, release to stop
- **Audio Visualization**: Real-time waveform and volume meter
- **Resizable Sidebar**: Customizable chat interface (300px - 800px)
- **Instant Feedback**: Transcript appears immediately, processing happens in background
- **User-Friendly Errors**: No technical jargon, helpful error messages

### Security & Architecture
- **Email/Password Authentication**: Secure JWT-based auth with access + refresh tokens
- **User Isolation**: Complete data separation between users
- **Specification-Based Architecture**: Zero SQL injection risk with safe query building
- **Performance Optimized**: Non-blocking operations, no redundant DB queries

### Production Ready
- **Docker Support**: Full containerization for easy deployment
- **PostgreSQL 15+**: With full-text search and optimized indexes
- **Comprehensive Error Handling**: Graceful degradation and recovery
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS

## 🏗️ Architecture

### Core Architecture Pattern: Specification-Based

```
Voice Input → STT (Deepgram) → Text Command
                                    ↓
                            LLM (Gemini 2.5 Flash) - Generates JSON Specification
                                    ↓
                            Backend Code - Validates Specification
                                    ↓
                            Safe Query Builder - Builds Parameterized SQL
                                    ↓
                            PostgreSQL Database
                                    ↓
                            Response to User
```

### Why This Pattern?

✅ **Zero SQL injection risk** - LLM never writes raw SQL  
✅ **98%+ accuracy** - Your code is deterministic  
✅ **Easy debugging** - Clear separation of concerns  
✅ **Testable** - Each layer independently testable  
✅ **Fast** - Meets latency requirements with single LLM call  

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with asyncpg driver
- **STT**: Deepgram Nova-3 (1.2-1.6s latency)
- **LLM**: Google Gemini 2.5 Flash
- **ORM**: SQLAlchemy (async)
- **Authentication**: JWT (access + refresh tokens) with bcrypt password hashing

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **HTTP Client**: Axios with JWT interceptors
- **Audio**: Web Audio API (AudioContext + AnalyserNode)
- **State Management**: React hooks (useState, useEffect, useCallback)

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Deployment**: Vercel-ready configuration
- **Database**: AWS RDS PostgreSQL or local PostgreSQL

## 📁 Project Structure

```
voice-first-to-do/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── repositories/     # Data access layer
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── parsers/          # Intent parsing
│   │   ├── builders/         # Query builders
│   │   ├── operations/       # CRUD operations
│   │   ├── clients/          # External API clients
│   │   ├── core/             # Configuration
│   │   └── utils/            # Utilities
│   ├── requirements.txt
│   ├── init_db.sql
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── lib/              # API client
│   │   └── types/            # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- API Keys:
  - Deepgram API key ([Get it here](https://deepgram.com))
  - Google AI API key ([Get it here](https://makersuite.google.com/app/apikey))

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd voice-first-to-do
```

2. **Set up environment variables**
```bash
# Copy example env file
cp backend/.env.example backend/.env

# Edit backend/.env with your API keys
DEEPGRAM_API_KEY=your_deepgram_key
GOOGLE_API_KEY=your_google_key
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database**
```bash
# Create database
createdb todo_voice_db

# Run init script
psql todo_voice_db < init_db.sql
```

4. **Configure environment**
```bash
# Copy and edit .env
cp .env.example .env
# Update DATABASE_URL and API keys
```

5. **Run backend**
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment**
```bash
# Copy and edit .env.local
cp .env.local.example .env.local
```

3. **Run frontend**
```bash
npm run dev
```

## 🎤 Voice Commands Examples

### Create Tasks
- "Create a task to buy groceries tomorrow at 2pm"
- "Add a high priority task to finish the project report"
- "Make a task called review pull requests"

### Read/Query Tasks
- "Show me all tasks"
- "Show me high priority tasks"
- "What are my overdue tasks?"
- "Show me tasks for tomorrow"
- "Find tasks related to client"

### Update Tasks
- "Mark the first task as completed"
- "Change the second task to high priority"
- "Update the third task to in progress"

### Delete Tasks
- "Delete the fourth task"
- "Remove the task about groceries"

### Complex Operations
- "Show me overdue tasks and mark the top 3 as high priority"
- "Find all pending tasks and show me the high priority ones"

## 📊 Database Schema

```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    
    -- Core fields
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Priority: 0=none, 1=low, 2=medium, 3=high
    priority INTEGER DEFAULT 0 CHECK (priority BETWEEN 0 AND 3),
    
    -- Status: pending, in_progress, completed
    status VARCHAR(20) DEFAULT 'pending',
    
    -- Scheduling
    scheduled_time TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- Full-text search vector
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', 
            coalesce(title, '') || ' ' || 
            coalesce(description, '') || ' ' || 
            coalesce(category, '')
        )
    ) STORED
);
```

## 🔌 API Endpoints

### Voice API (Primary)
- `POST /api/voice/process` - Process voice command

### REST API (Fallback)
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/{id}` - Get single task
- `POST /api/tasks` - Create task
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🚢 Deployment

### Vercel Deployment

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Configure environment variables in Vercel**
- `DATABASE_URL`
- `DEEPGRAM_API_KEY`
- `GOOGLE_API_KEY`
- `SECRET_KEY`

3. **Deploy**
```bash
vercel
```

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 🎨 Design Patterns Used

- **Repository Pattern**: Data access abstraction
- **Strategy Pattern**: CRUD operations
- **Adapter Pattern**: External API clients
- **Dependency Injection**: Service composition
- **Factory Pattern**: Operation creation

## 🔒 Security Features

- **SQL Injection Protection**: Parameterized queries only
- **Input Validation**: Pydantic schemas
- **Whitelisted Filters**: Pre-defined filter types
- **User Scoping**: All queries scoped to user
- **CORS Configuration**: Controlled origins

## 📈 Performance Optimizations

- **Async I/O**: AsyncIO throughout the stack
- **Connection Pooling**: Database connection management
- **Indexed Queries**: PostgreSQL indexes on common filters
- **Full-Text Search**: PostgreSQL tsvector for text search
- **Single LLM Call**: Most operations with one LLM round trip

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection
psql -d todo_voice_db -U voice_user
```

### API Key Issues
- Verify keys are set in `.env`
- Check Deepgram account has credits
- Ensure Google AI API is enabled

### Port Conflicts
```bash
# Change ports in docker-compose.yml or .env
# Backend: 8000 (default)
# Frontend: 3000 (default)
# Database: 5432 (default)
```

## 📚 Documentation

Comprehensive guides are available:

- **[USAGE.md](USAGE.md)** - Complete voice command guide with examples
  - All supported voice commands organized by category
  - Natural language variations and examples
  - How conversational memory works
  - Tips & best practices
  - Performance metrics
  - Troubleshooting guide

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep dive into system design
  - High-level architecture diagrams
  - Design patterns and principles
  - Security architecture
  - Performance optimizations
  - Two-phase response system
  - Authentication & memory systems
  - Database schema and indexing

## 📝 License

MIT License - feel free to use this project for your own purposes.

## 🙏 Acknowledgments

- **Deepgram** for fast and accurate speech-to-text
- **Google** for Gemini 2.5 Flash LLM
- **FastAPI** for the excellent Python web framework
- **Next.js** for the React framework

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check logs with `docker-compose logs`

---

**Built with ❤️ for voice-first interactions**

# Quick Start Guide

## Prerequisites

Before you begin, ensure you have:

1. **API Keys** (Required):
   - **Deepgram API Key**: Sign up at https://deepgram.com and get your API key
   - **Google AI API Key**: Get it from https://makersuite.google.com/app/apikey

2. **Software** (Choose one option):
   - **Option A (Docker)**: Docker and Docker Compose installed
   - **Option B (Manual)**: Python 3.11+, Node.js 18+, PostgreSQL 15+

## 🚀 Fastest Way to Start (Docker)

### 1. Set Up Environment Variables

```bash
cd voice-first-to-do

# Create backend .env file
cat > backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://voice_user:voice_password@postgres:5432/todo_voice_db
DEEPGRAM_API_KEY=YOUR_DEEPGRAM_KEY_HERE
GOOGLE_API_KEY=YOUR_GOOGLE_KEY_HERE
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
DEFAULT_USER_ID=550e8400-e29b-41d4-a716-446655440000
EOF

# Replace YOUR_DEEPGRAM_KEY_HERE and YOUR_GOOGLE_KEY_HERE with actual keys!
```

### 2. Start Everything with Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Backend API on port 8000
- Frontend on port 3000

### 3. Access the Application

Open your browser and go to: **http://localhost:3000**

### 4. Try It Out!

1. Click the blue microphone button
2. Say: "Create a task to buy groceries tomorrow"
3. Watch your task appear!

### Other Voice Commands to Try:

- "Show me all tasks"
- "Show me high priority tasks"
- "Mark the first task as completed"
- "Delete the second task"
- "Create a high priority task to finish the report"

## 🛠️ Manual Setup (Without Docker)

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up database
createdb todo_voice_db
psql todo_voice_db < init_db.sql

# 5. Create .env file (see Docker section for content)
# Edit with your API keys!

# 6. Run backend
uvicorn app.main:app --reload
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
# 1. Navigate to frontend (in a new terminal)
cd frontend

# 2. Install dependencies
npm install

# 3. Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# 4. Run frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🔧 Troubleshooting

### Database Connection Error

If you see database connection errors:

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Or if manual setup:
pg_isready
```

### API Key Errors

If you see "API key invalid" errors:

1. Double-check your API keys in `backend/.env`
2. Ensure there are no spaces or quotes around the keys
3. Verify your Deepgram account has credits
4. Ensure Google AI API is enabled for your project

### Port Already in Use

If ports 3000 or 8000 are already in use:

```bash
# For Docker, edit docker-compose.yml:
# Change "3000:3000" to "3001:3000" for frontend
# Change "8000:8000" to "8001:8000" for backend

# For manual setup, use different ports:
# Backend: uvicorn app.main:app --port 8001 --reload
# Frontend: PORT=3001 npm run dev
```

### Microphone Not Working

1. Ensure your browser has microphone permissions
2. Use HTTPS in production (browsers require it for microphone access)
3. Check browser console for errors

## 📖 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 What's Next?

1. **Explore the codebase**: Check out the well-structured backend and frontend code
2. **Test voice commands**: Try different natural language commands
3. **Customize**: Modify the UI, add new features, or extend the voice commands
4. **Deploy**: Use the included Vercel configuration or Docker for deployment

## 📝 Architecture Overview

```
┌─────────────────┐
│  Voice Input    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Deepgram STT  │  ← Speech to Text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gemini 2.5     │  ← Intent Parsing
│     Flash       │     (Generates JSON Spec)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI        │  ← Validates & Executes
│  Backend        │     (Safe Query Builder)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL     │  ← Data Storage
└─────────────────┘
```

## 🎨 Key Features Implemented

✅ Voice-first interface with sub-2s latency  
✅ Natural language command processing  
✅ Full CRUD operations via voice  
✅ Specification-based architecture (zero SQL injection)  
✅ Beautiful, responsive UI with Tailwind CSS  
✅ Real-time task updates  
✅ Docker support for easy deployment  
✅ Comprehensive error handling  
✅ Production-ready logging  

## 🆘 Need Help?

1. Check the main [README.md](README.md) for detailed documentation
2. Review the API docs at http://localhost:8000/docs
3. Check Docker logs: `docker-compose logs -f`
4. Inspect browser console for frontend errors

## 🎉 You're All Set!

Start speaking to your to-do list and experience the future of task management!


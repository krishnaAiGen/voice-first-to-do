# Setup Instructions

## Backend Setup (Python)

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

```bash
# Copy the example file
cp env.example .env

# Edit .env with your actual API keys
nano .env
# or
vim .env
# or use any text editor
```

**Required API Keys:**
- **DEEPGRAM_API_KEY**: Get from https://deepgram.com (sign up for free tier)
- **GOOGLE_API_KEY**: Get from https://makersuite.google.com/app/apikey

Edit `.env` to look like this:
```bash
DATABASE_URL=postgresql+asyncpg://voice_user:voice_password@localhost:5432/todo_voice_db
DEEPGRAM_API_KEY=abc123your_actual_deepgram_key_here
GOOGLE_API_KEY=xyz789your_actual_google_key_here
SECRET_KEY=change-this-to-a-random-string
ENVIRONMENT=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
DEFAULT_USER_ID=550e8400-e29b-41d4-a716-446655440000
```

### 5. Set Up PostgreSQL Database

#### Option A: Using Docker (Recommended)

```bash
# Start just the PostgreSQL container
docker run -d \
  --name voice-todo-postgres \
  -e POSTGRES_USER=voice_user \
  -e POSTGRES_PASSWORD=voice_password \
  -e POSTGRES_DB=todo_voice_db \
  -p 5432:5432 \
  postgres:15-alpine

# Wait a few seconds for it to start, then initialize the database
docker exec -i voice-todo-postgres psql -U voice_user -d todo_voice_db < init_db.sql
```

#### Option B: Using Local PostgreSQL

```bash
# Create database
createdb todo_voice_db

# Run initialization script
psql todo_voice_db < init_db.sql
```

### 6. Start the Backend Server

#### Method 1: Using Uvicorn Directly (Recommended)

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Method 2: Using Python Module

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Method 3: Running main.py Directly

```bash
python app/main.py
```

The backend will start on **http://localhost:8000**

### 7. Verify Backend is Running

Open your browser and visit:
- **API Root**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Frontend Setup (Node.js)

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Node Dependencies

```bash
npm install
```

### 3. Create Environment File

```bash
# Copy the example file
cp env.example .env.local

# The default values should work if backend is on localhost:8000
# Edit if needed
```

### 4. Start the Frontend Server

```bash
npm run dev
```

The frontend will start on **http://localhost:3000**

### 5. Verify Frontend is Running

Open your browser and visit: **http://localhost:3000**

You should see the Voice-First To-Do interface!

## Quick Test

1. **Open** http://localhost:3000 in your browser
2. **Click** the blue microphone button
3. **Say**: "Create a task to buy groceries"
4. **Watch** your task appear!

## Common Issues & Solutions

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**: Make sure virtual environment is activated and dependencies are installed
```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt
```

---

**Error**: `Connection refused` or database errors

**Solution**: Make sure PostgreSQL is running
```bash
# Check if PostgreSQL is running
pg_isready

# If using Docker:
docker ps | grep postgres
```

---

**Error**: `API key invalid` or `Authentication failed`

**Solution**: Check your `.env` file has correct API keys
```bash
cat .env | grep API_KEY
# Should show your actual keys, not "your_key_here"
```

### Frontend Won't Start

**Error**: `Cannot find module` or package errors

**Solution**: Delete node_modules and reinstall
```bash
rm -rf node_modules
npm install
```

---

**Error**: `Port 3000 already in use`

**Solution**: Use a different port
```bash
PORT=3001 npm run dev
```

### Can't Connect to Backend

**Error**: Frontend shows API connection errors

**Solution**: Check `.env.local` has correct backend URL
```bash
cat .env.local
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Directory Structure After Setup

```
voice-first-to-do/
├── backend/
│   ├── venv/                 # ← Virtual environment (created)
│   ├── .env                  # ← Your environment file (created)
│   ├── env.example           # Template
│   └── ...
└── frontend/
    ├── node_modules/         # ← Node packages (created)
    ├── .env.local            # ← Your environment file (created)
    ├── env.example           # Template
    └── ...
```

## What Ports Are Used?

- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432

## Next Steps

1. ✅ Backend running on http://localhost:8000
2. ✅ Frontend running on http://localhost:3000
3. ✅ Database initialized with sample data
4. 🎤 Start using voice commands!

## API Keys Setup Guide

### Getting Deepgram API Key

1. Go to https://deepgram.com
2. Click "Sign Up" (free tier available)
3. Verify your email
4. Go to https://console.deepgram.com/
5. Navigate to "API Keys"
6. Create a new key or use the default key
7. Copy the key to your `.env` file

### Getting Google AI (Gemini) API Key

1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

Both services offer free tiers that are sufficient for development and testing!

## Running Everything with Docker (Alternative)

If you prefer Docker, you can skip the manual setup:

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

This starts:
- PostgreSQL database
- Backend API
- Frontend UI

All configured and ready to use!


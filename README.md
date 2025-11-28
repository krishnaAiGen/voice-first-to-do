# Voice-First To-Do List 🎙️

A voice-controlled to-do list application with **sub-2 second latency** and **90%+ accuracy**. Manage your tasks naturally using voice commands.

## 🚀 Quick Start

### Try the Live App

👉 **[https://voice-first-to-do.vercel.app/](https://voice-first-to-do.vercel.app/)**

1. **Sign Up** with your email, name, and password
2. **Hold the Option key** (Alt on Windows) to start recording
3. **Release the Option key** to stop recording and process your command
4. **View your tasks** updated in real-time!

### Example Voice Commands

- "Create a task to buy groceries tomorrow at 2pm"
- "Show me all my tasks"
- "Mark my grocery task as completed"
- "Delete the 3rd task"
- "Move my meeting to next Monday"
- "Show overdue tasks"

---

## 🔧 Setup Your Own Instance

### Prerequisites

- PostgreSQL 15+ database
- Deepgram API key ([get one here](https://deepgram.com))
- Google Gemini API key ([get one here](https://aistudio.google.com/app/apikey))

### Database Configuration

Create a PostgreSQL database and configure these environment variables in your **backend**:

```env
# Database Connection
postgres_host=your-db-host.amazonaws.com
postgres_port=5432
postgres_database=your_database_name
postgres_user=your_username
postgres_password=your_password

# API Keys
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### Installation

#### Backend

```bash
cd backend
pip install -r requirements.txt

# Copy and configure environment
cp env.example .env
# Edit .env with your database credentials and API keys

# Run migrations to create tables
python scripts/migrate_add_users.py

# Start backend
python -m app.main
```

Backend will run on **http://localhost:3002**

#### Frontend

```bash
cd frontend
npm install

# Copy and configure environment
cp env.example .env
# Edit .env to point to your backend

# Start frontend
npm run dev
```

Frontend will run on **http://localhost:3000**

---

## 📖 Documentation

For detailed information, see:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and technical details
- **[USAGE.md](USAGE.md)** - Complete guide to voice commands and features
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide (AWS + Vercel)
- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Detailed setup and configuration

---

## 🎯 Key Features

- **Voice-First Interface**: Natural language voice commands for all operations
- **Sub-2s Latency**: Two-phase response (transcript in ~1.5s, full processing in ~3s)
- **Keyboard Shortcuts**: Hold Option/Alt to record, release to stop
- **Audio Visualization**: Real-time waveform and volume meter
- **User Authentication**: Secure email/password login with JWT
- **Conversational Memory**: Remembers last 5 messages for context
- **Smart Intent Parsing**: 90%+ accuracy with Gemini 2.5 Flash
- **Beautiful UI**: Modern, responsive design with resizable sidebar

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL 15+** - Database with full-text search
- **Deepgram Nova-3** - Speech-to-Text (STT)
- **Gemini 2.5 Flash** - LLM for intent parsing
- **SQLAlchemy 2.0** - Async ORM
- **JWT Authentication** - Secure user sessions

### Frontend
- **Next.js 14** - React framework
- **Tailwind CSS** - Styling
- **Axios** - API client
- **Web Audio API** - Real-time audio visualization

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙋 Support

For issues, questions, or feature requests, please open an issue on GitHub.

---

**Built with ❤️ using voice-first design principles**

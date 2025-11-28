# Deployment Guide

Complete guide for deploying Voice-First To-Do to AWS (Backend) and Vercel (Frontend).

## Table of Contents

1. [Local Vercel Build](#local-vercel-build)
2. [Backend Deployment (AWS EC2)](#backend-deployment-aws-ec2)
3. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
4. [CORS Configuration](#cors-configuration)
5. [Environment Variables](#environment-variables)
6. [Testing](#testing)

---

## Local Vercel Build

Run the same build process that Vercel uses:

### **Step 1: Install Dependencies**
```bash
cd frontend
npm install
```

### **Step 2: Create Production .env**
```bash
# Create .env.production
cat > .env.production << EOF
NEXT_PUBLIC_API_URL=http://16.171.111.4:3002/api
EOF
```

### **Step 3: Run Vercel Build Locally**
```bash
# Clean previous builds
npm run clean

# Build for production (same as Vercel)
npm run build

# Test production build locally
npm run start
```

### **Step 4: Access Local Production Build**
- Open http://localhost:3000
- Should connect to AWS backend at 16.171.111.4:3002

---

## Backend Deployment (AWS EC2)

### **Your Server Details**
- IP: `16.171.111.4`
- Backend Port: `3002`
- API Endpoint: `http://16.171.111.4:3002/api`

### **Step 1: Connect to AWS Server**
```bash
ssh ubuntu@16.171.111.4
```

### **Step 2: Setup Backend**
```bash
# Navigate to project
cd /home/ubuntu/projects/voice-first-to-do/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **Step 3: Configure Environment**
Create `/home/ubuntu/projects/voice-first-to-do/backend/.env`:

```bash
# Database (AWS RDS or local PostgreSQL)
postgres_host=your-rds-endpoint.amazonaws.com
postgres_port=5432
postgres_database=todo_voice_db
postgres_user=your_user
postgres_password=your_password

# External API Keys
DEEPGRAM_API_KEY=your_deepgram_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here

# Security
SECRET_KEY=your-super-secret-production-key-change-this
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS - CRITICAL: Add your Vercel domain!
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app,https://your-app-git-main.vercel.app

# Conversation
CONVERSATION_HISTORY=5
DEFAULT_USER_ID=550e8400-e29b-41d4-a716-446655440000
```

### **Step 4: Run with Gunicorn (Production)**

#### **Install Gunicorn**
```bash
pip install gunicorn
```

#### **Start Backend**
```bash
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:3002 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --daemon
```

#### **Or Run with Screen (Persistent)**
```bash
# Start screen session
screen -S backend

# Run gunicorn
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:3002 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -

# Detach: Ctrl+A, then D
# Reattach: screen -r backend
```

### **Step 5: Setup Systemd Service (Recommended)**

Create `/etc/systemd/system/voice-todo-backend.service`:

```ini
[Unit]
Description=Voice-First To-Do Backend API
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/projects/voice-first-to-do/backend
Environment="PATH=/home/ubuntu/projects/voice-first-to-do/backend/venv/bin"
ExecStart=/home/ubuntu/projects/voice-first-to-do/backend/venv/bin/gunicorn \
    app.main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:3002 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable voice-todo-backend
sudo systemctl start voice-todo-backend
sudo systemctl status voice-todo-backend
```

### **Step 6: Configure Security Group (AWS)**

In AWS Console → EC2 → Security Groups:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| Custom TCP | TCP | 3002 | 0.0.0.0/0 | Backend API |
| SSH | TCP | 22 | Your IP | SSH access |
| PostgreSQL | TCP | 5432 | Backend SG | Database (if using RDS) |

---

## Frontend Deployment (Vercel)

### **Option 1: Vercel CLI (Recommended)**

#### **Install Vercel CLI**
```bash
npm install -g vercel
```

#### **Login to Vercel**
```bash
vercel login
```

#### **Deploy from Frontend Directory**
```bash
cd frontend

# First deployment (link project)
vercel

# Production deployment
vercel --prod
```

#### **Set Environment Variables**

During deployment, Vercel will ask for environment variables, or set them in dashboard:

```bash
# Via CLI
vercel env add NEXT_PUBLIC_API_URL production

# Enter: http://16.171.111.4:3002/api
```

### **Option 2: GitHub Integration**

1. **Push to GitHub:**
```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

2. **Connect to Vercel:**
   - Go to https://vercel.com
   - Click "Add New Project"
   - Import your GitHub repository
   - Set Root Directory: `frontend`
   - Add environment variables:
     ```
     NEXT_PUBLIC_API_URL=http://16.171.111.4:3002/api
     ```
   - Deploy!

3. **Auto-Deploy:**
   - Every push to `main` branch will auto-deploy

---

## CORS Configuration

### **Critical: Update Backend CORS**

Your backend `.env` **MUST** include all frontend origins:

```bash
# Example if your Vercel app is: https://voice-todo.vercel.app
CORS_ORIGINS=http://localhost:3000,https://voice-todo.vercel.app,https://voice-todo-git-main.vercel.app,https://voice-todo-*.vercel.app
```

### **Common CORS Issues:**

#### **Issue 1: Missing Vercel Domain**
```bash
# ❌ Wrong - Missing production domain
CORS_ORIGINS=http://localhost:3000

# ✅ Correct - Includes production
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
```

#### **Issue 2: Wrong Protocol**
```bash
# ❌ Wrong - Vercel uses HTTPS
CORS_ORIGINS=http://your-app.vercel.app

# ✅ Correct
CORS_ORIGINS=https://your-app.vercel.app
```

#### **Issue 3: Trailing Slash**
```bash
# ❌ Wrong
CORS_ORIGINS=https://your-app.vercel.app/

# ✅ Correct
CORS_ORIGINS=https://your-app.vercel.app
```

### **After Updating CORS:**
```bash
# Restart backend
sudo systemctl restart voice-todo-backend

# Or if using screen/manual
pkill -f gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:3002
```

---

## Environment Variables

### **Backend (.env on AWS Server)**
```bash
# Database
postgres_host=your-db-host.amazonaws.com
postgres_port=5432
postgres_database=todo_voice_db
postgres_user=postgres
postgres_password=your_password

# API Keys (REQUIRED)
DEEPGRAM_API_KEY=your_deepgram_key
GOOGLE_API_KEY=your_google_key

# Security
SECRET_KEY=random-string-min-32-chars-production-only
ENVIRONMENT=production
LOG_LEVEL=INFO

# CORS (CRITICAL - Update with your Vercel domain!)
CORS_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app

# Application
CONVERSATION_HISTORY=5
DEFAULT_USER_ID=550e8400-e29b-41d4-a716-446655440000
```

### **Frontend (Vercel Dashboard or .env.production)**
```bash
NEXT_PUBLIC_API_URL=http://16.171.111.4:3002/api
```

---

## Testing

### **Test Backend Health**
```bash
# From your local machine
curl http://16.171.111.4:3002/health

# Expected response:
# {"status":"healthy","environment":"production"}
```

### **Test CORS**
```bash
curl -I -X OPTIONS \
  -H "Origin: https://your-app.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  http://16.171.111.4:3002/api/auth/login

# Should see:
# Access-Control-Allow-Origin: https://your-app.vercel.app
# Access-Control-Allow-Credentials: true
```

### **Test API Endpoints**
```bash
# Test docs (if ENVIRONMENT=development)
open http://16.171.111.4:3002/docs

# Test login
curl -X POST http://16.171.111.4:3002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### **Test Frontend**
1. Open your Vercel URL: `https://your-app.vercel.app`
2. Try to login
3. Check browser console for errors
4. Verify API calls go to `http://16.171.111.4:3002/api`

---

## Troubleshooting

### **Backend Issues**

#### **Port Already in Use**
```bash
# Find process using port 3002
sudo lsof -i :3002

# Kill process
sudo kill -9 <PID>
```

#### **Check Backend Logs**
```bash
# If using systemd
sudo journalctl -u voice-todo-backend -f

# If using screen
screen -r backend

# If running manually
tail -f /var/log/voice-todo-backend.log
```

#### **Database Connection Failed**
```bash
# Test database connection
psql -h your-db-host.amazonaws.com -U postgres -d todo_voice_db

# Check if tables exist
\dt
```

### **Frontend Issues**

#### **Build Fails on Vercel**
- Check build logs in Vercel dashboard
- Verify environment variables are set
- Try building locally: `npm run build`

#### **CORS Errors**
- Verify `CORS_ORIGINS` includes your Vercel domain
- Restart backend after updating CORS
- Check browser console for exact error

#### **Can't Connect to Backend**
- Verify backend is running: `curl http://16.171.111.4:3002/health`
- Check AWS Security Group allows port 3002
- Verify `NEXT_PUBLIC_API_URL` is correct

---

## Monitoring

### **Backend Monitoring**
```bash
# Check if backend is running
sudo systemctl status voice-todo-backend

# View logs
sudo journalctl -u voice-todo-backend -n 100

# Check resource usage
htop
```

### **Vercel Monitoring**
- Dashboard: https://vercel.com
- View deployment logs
- Check analytics
- Monitor errors

---

## Rollback

### **Backend Rollback**
```bash
# Stop current version
sudo systemctl stop voice-todo-backend

# Checkout previous version
git checkout <previous-commit>

# Restart
sudo systemctl start voice-todo-backend
```

### **Frontend Rollback**
In Vercel dashboard:
1. Go to Deployments
2. Find previous working deployment
3. Click "Promote to Production"

---

## Performance Optimization

### **Backend**
- Use 4 Gunicorn workers (2 × CPU cores)
- Enable caching with Redis (future)
- Use connection pooling (already configured)
- Monitor with Prometheus/Grafana (future)

### **Frontend**
- Vercel Edge Network (automatic)
- Image optimization (Next.js automatic)
- Code splitting (Next.js automatic)
- Static page generation where possible

---

## Security Checklist

- ✅ Change `SECRET_KEY` to random string (min 32 chars)
- ✅ Use HTTPS for frontend (Vercel automatic)
- ✅ Restrict CORS origins (no wildcards in production)
- ✅ Use environment variables for secrets
- ✅ Enable AWS Security Groups
- ✅ Use strong database passwords
- ✅ Keep dependencies updated (`npm audit fix`)
- ✅ Enable rate limiting (future enhancement)

---

## Quick Reference

### **Backend Commands**
```bash
# Start
sudo systemctl start voice-todo-backend

# Stop
sudo systemctl stop voice-todo-backend

# Restart
sudo systemctl restart voice-todo-backend

# View logs
sudo journalctl -u voice-todo-backend -f
```

### **Frontend Commands**
```bash
# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls
```

### **Useful URLs**
- Backend API: http://16.171.111.4:3002
- Backend Health: http://16.171.111.4:3002/health
- Backend Docs: http://16.171.111.4:3002/docs (if development)
- Frontend: https://your-app.vercel.app

---

## Support

For issues:
1. Check logs (backend and frontend)
2. Verify environment variables
3. Test backend health endpoint
4. Check CORS configuration
5. Review security groups (AWS)

---

**Your Deployment Setup:**
- ✅ Backend: AWS EC2 at `16.171.111.4:3002`
- ✅ Frontend: Vercel at `https://your-app.vercel.app`
- ✅ Database: AWS RDS PostgreSQL
- ✅ Security: JWT authentication
- ✅ Performance: Gunicorn + Next.js optimizations


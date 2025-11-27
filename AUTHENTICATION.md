# Authentication System Setup Guide

## 🔐 Overview

The Voice-First To-Do app now includes a complete authentication system with:
- Email + password authentication
- JWT tokens (access & refresh)
- Secure password hashing (bcrypt)
- Chat history persistence per user
- Protected API endpoints

## 📊 Database Schema

### New Tables

#### `users`
- Stores user accounts
- Email (unique, lowercase)
- Hashed passwords
- Display names
- Account status

#### `chat_messages`
- Stores conversation history
- Links to users via foreign key
- Supports user, assistant, and error messages
- Includes latency metrics

#### `refresh_tokens`
- Manages JWT refresh tokens
- Enables secure token rotation
- Supports logout functionality

### Updated Tables

#### `toDoList`
- Added foreign key to `users` table
- Cascading delete (tasks deleted when user is deleted)

## 🚀 Setup Instructions

### 1. Run Database Migration

```bash
cd backend
python run_migration.py
```

Or manually using psql:

```bash
psql -h your-host -U your-user -d your-database -f migrations/001_add_authentication.sql
```

### 2. Verify Migration

Check that the tables were created:

```sql
\dt  -- List tables
\d users  -- Describe users table
\d chat_messages  -- Describe chat_messages table
```

### 3. Test User Account

A default test account is created automatically:
- **Email**: `test@example.com`
- **Password**: `password123`

### 4. Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 5. Start Frontend

```bash
cd frontend
npm run dev
```

## 🔑 API Endpoints

### Public Endpoints (No Auth Required)

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123",
  "display_name": "John Doe"  // optional
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "abc123...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "display_name": "John Doe"
  }
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response:** Same as register

### Protected Endpoints (Require Auth)

All requests must include:
```http
Authorization: Bearer <access_token>
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### Process Voice Command
```http
POST /api/voice/process
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "audio_base64": "..."
}
```

#### Get Tasks
```http
GET /api/tasks
Authorization: Bearer <access_token>
```

#### Get Chat History
```http
GET /api/chat/history?limit=50&offset=0
Authorization: Bearer <access_token>
```

#### Clear Chat History
```http
DELETE /api/chat/history
Authorization: Bearer <access_token>
```

## 🔧 Frontend Integration

### Login Flow

1. User enters email/password in `LoginForm` component
2. Frontend calls `/api/auth/login` or `/api/auth/register`
3. Backend returns JWT tokens
4. Frontend stores tokens in localStorage:
   - `access_token`
   - `refresh_token`
   - `user` (JSON)
5. Frontend redirects to main app

### Authenticated Requests

The axios interceptor automatically adds the JWT token to all requests:

```typescript
// Automatic token injection
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Token Expiration Handling

If a request returns 401 (Unauthorized):
1. Axios interceptor catches the error
2. Clears localStorage
3. Redirects to login page

### Logout Flow

```typescript
const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  // Redirect to login
};
```

## 📋 Database Structure Diagram

```
┌─────────────────┐
│     users       │
├─────────────────┤
│ id (PK)         │◄────┐
│ email (UNIQUE)  │     │
│ hashed_password │     │
│ display_name    │     │
│ is_active       │     │
│ created_at      │     │
│ last_login_at   │     │
└─────────────────┘     │
                        │ FK: user_id
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  toDoList   │  │chat_messages │  │refresh_tokens│
├─────────────┤  ├──────────────┤  ├──────────────┤
│ id (PK)     │  │ id (PK)      │  │ id (PK)      │
│ user_id FK  │  │ user_id FK   │  │ user_id FK   │
│ title       │  │ type         │  │ token        │
│ ...         │  │ content      │  │ expires_at   │
└─────────────┘  │ transcript   │  │ revoked      │
                 │ latency_ms   │  └──────────────┘
                 └──────────────┘
```

## 🔒 Security Features

### Password Security
- Passwords hashed with bcrypt
- Minimum 8 characters required
- Salt automatically generated

### JWT Tokens
- Access tokens expire after 30 minutes
- Refresh tokens expire after 7 days
- Tokens signed with SECRET_KEY from settings

### Email Normalization
- All emails automatically lowercased
- Ensures case-insensitive matching

### Protected Routes
- All task and voice endpoints require authentication
- 401 responses trigger automatic logout

## 🧪 Testing

### Test Registration
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "testpass123",
    "display_name": "Test User"
  }'
```

### Test Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Test Protected Endpoint
```bash
# Replace TOKEN with actual access_token from login response
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN"
```

## 📱 Frontend User Flow

### First Time User
1. Visits app
2. Sees login form
3. Clicks "Don't have an account? Sign up"
4. Enters email, password, display name
5. Clicks "Create Account"
6. Automatically logged in and redirected to main app

### Returning User
1. Visits app
2. App checks localStorage for `access_token`
3. If found: Automatically logged in
4. If not found: Shows login form

### User Experience
- Clean, modern login UI
- Loading states for all actions
- Error messages for failed attempts
- "Remember me" via localStorage persistence
- Instant logout with token cleanup

## 🐛 Troubleshooting

### Migration Fails
```bash
# Check database connection
python -c "from app.core.config import settings; print(settings.database_url)"

# Verify table doesn't exist already
psql -h host -U user -d db -c "\dt users"
```

### 401 Errors
- Check token is being sent in Authorization header
- Verify token hasn't expired (30 min lifetime)
- Ensure SECRET_KEY matches between sessions

### Chat History Not Loading
- Verify user is authenticated
- Check browser console for errors
- Ensure `/api/chat/history` endpoint returns data

### Tasks Not Showing
- Confirm user_id foreign key relationship is correct
- Check if tasks belong to the authenticated user
- Verify `/api/tasks` endpoint requires authentication

## 🎉 Success!

Once migration is complete, users can:
- ✅ Register with email/password
- ✅ Login securely
- ✅ Access their personal tasks
- ✅ View chat history
- ✅ Use voice commands (authenticated)
- ✅ Logout safely

Each user has their own isolated data!


-- ============================================
-- Migration 001: Add Authentication & Chat History
-- ============================================

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. USERS TABLE (Authentication)
-- ============================================
CREATE TABLE IF NOT EXISTS "users" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = TRUE;

-- Auto-update updated_at trigger
CREATE OR REPLACE FUNCTION update_users_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS users_updated_at_trigger ON users;
CREATE TRIGGER users_updated_at_trigger
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_users_updated_at();


-- ============================================
-- 2. REFRESH TOKENS TABLE (JWT Management)
-- ============================================
CREATE TABLE IF NOT EXISTS "refresh_tokens" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token) WHERE revoked = FALSE;


-- ============================================
-- 3. CHAT MESSAGES TABLE (Chat History)
-- ============================================
CREATE TABLE IF NOT EXISTS "chat_messages" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'assistant', 'error')),
    content TEXT NOT NULL,
    transcript TEXT,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast retrieval
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_time ON chat_messages(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_type ON chat_messages(user_id, message_type);


-- ============================================
-- 4. CREATE DEFAULT TEST USER (BEFORE FK Constraint)
-- ============================================
-- Password: "password123" (bcrypt hash)
-- Create test user FIRST so we can reference it
INSERT INTO users (id, email, hashed_password, display_name, is_active) 
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'test@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Y3W5V9U.YO4W',
    'Test User',
    TRUE
) ON CONFLICT (email) DO NOTHING;


-- ============================================
-- 5. UPDATE EXISTING TASKS (Before FK Constraint)
-- ============================================
-- Update existing tasks to belong to test user
-- This ensures existing data doesn't break when we add FK constraint
UPDATE "toDoList" 
SET user_id = '550e8400-e29b-41d4-a716-446655440000'
WHERE user_id IS NULL 
   OR user_id NOT IN (SELECT id FROM users);


-- ============================================
-- 6. UPDATE TODO LIST TABLE (Add FK Constraint)
-- ============================================
-- Add foreign key to existing toDoList table (AFTER user exists and tasks are updated)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_todolist_user'
    ) THEN
        ALTER TABLE "toDoList" 
        ADD CONSTRAINT fk_todolist_user 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
    END IF;
END $$;


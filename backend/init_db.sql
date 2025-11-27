-- Initialize PostgreSQL database for Voice-First To-Do

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create toDoList table
CREATE TABLE IF NOT EXISTS "toDoList" (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    
    -- Core fields
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Priority: 0=none, 1=low, 2=medium, 3=high
    priority INTEGER DEFAULT 0 CHECK (priority BETWEEN 0 AND 3),
    
    -- Status: pending, in_progress, completed
    status VARCHAR(20) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'in_progress', 'completed')),
    
    -- Scheduling
    scheduled_time TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- For display ordering
    display_order INTEGER,
    
    -- Full-text search vector
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', 
            coalesce(title, '') || ' ' || 
            coalesce(description, '') || ' ' || 
            coalesce(category, '')
        )
    ) STORED
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_todolist_user_id ON "toDoList"(user_id);
CREATE INDEX IF NOT EXISTS idx_todolist_scheduled ON "toDoList"(user_id, scheduled_time) 
    WHERE scheduled_time IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_todolist_status ON "toDoList"(user_id, status);
CREATE INDEX IF NOT EXISTS idx_todolist_priority ON "toDoList"(user_id, priority);
CREATE INDEX IF NOT EXISTS idx_todolist_category ON "toDoList"(user_id, category);
CREATE INDEX IF NOT EXISTS idx_todolist_search ON "toDoList" USING GIN(search_vector);
CREATE INDEX IF NOT EXISTS idx_todolist_created ON "toDoList"(created_at);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_todolist_updated_at ON "toDoList";
CREATE TRIGGER update_todolist_updated_at 
    BEFORE UPDATE ON "toDoList"
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample tasks for testing
INSERT INTO "toDoList" (user_id, title, description, priority, status, scheduled_time)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'Buy groceries', 'Get milk, eggs, and bread', 2, 'pending', NOW() + INTERVAL '1 day'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Finish project report', 'Complete quarterly report for Q4', 3, 'in_progress', NOW() + INTERVAL '2 days'),
    ('550e8400-e29b-41d4-a716-446655440000', 'Call dentist', 'Schedule appointment for cleaning', 1, 'pending', NULL),
    ('550e8400-e29b-41d4-a716-446655440000', 'Review pull requests', 'Check team code reviews', 2, 'pending', NOW() + INTERVAL '3 hours')
ON CONFLICT DO NOTHING;


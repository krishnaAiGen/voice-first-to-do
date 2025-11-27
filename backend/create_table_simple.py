"""
Simple script to create the toDoList table
Run this to initialize your database
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def create_table():
    """Create toDoList table in PostgreSQL"""
    
    # Build connection string from env vars
    host = os.getenv('postgres_host')
    port = os.getenv('postgres_port', '5432')
    database = os.getenv('postgres_database')
    user = os.getenv('postgres_user')
    password = os.getenv('postgres_password')
    
    # Or use DATABASE_URL if available
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        database_url = f'postgresql://{user}:{password}@{host}:{port}/{database}'
        # Remove the +asyncpg part for asyncpg
        database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    else:
        database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print("=" * 60)
    print("Creating toDoList Table")
    print("=" * 60)
    print(f"\nConnecting to: {host}:{port}/{database}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✅ Connected successfully!\n")
        
        # Read SQL file
        with open('init_db.sql', 'r') as f:
            sql = f.read()
        
        print("📋 Executing SQL script...")
        
        # Execute SQL (asyncpg doesn't support multiple statements at once)
        # So we'll create the table manually
        
        await conn.execute('''
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp"
        ''')
        print("✅ Created uuid-ossp extension")
        
        await conn.execute('''
            CREATE EXTENSION IF NOT EXISTS "pg_trgm"
        ''')
        print("✅ Created pg_trgm extension")
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS "toDoList" (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL,
                
                title VARCHAR(500) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                
                priority INTEGER DEFAULT 0 CHECK (priority BETWEEN 0 AND 3),
                status VARCHAR(20) DEFAULT 'pending' 
                    CHECK (status IN ('pending', 'in_progress', 'completed')),
                
                scheduled_time TIMESTAMPTZ,
                
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                completed_at TIMESTAMPTZ,
                
                display_order INTEGER,
                
                search_vector tsvector GENERATED ALWAYS AS (
                    to_tsvector('english', 
                        coalesce(title, '') || ' ' || 
                        coalesce(description, '') || ' ' || 
                        coalesce(category, '')
                    )
                ) STORED
            )
        ''')
        print("✅ Created toDoList table")
        
        # Create indexes
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_todolist_user_id ON "toDoList"(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_todolist_status ON "toDoList"(user_id, status)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_todolist_priority ON "toDoList"(user_id, priority)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_todolist_search ON "toDoList" USING GIN(search_vector)')
        print("✅ Created indexes")
        
        # Create trigger function
        await conn.execute('''
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        ''')
        
        await conn.execute('DROP TRIGGER IF EXISTS update_todolist_updated_at ON "toDoList"')
        await conn.execute('''
            CREATE TRIGGER update_todolist_updated_at 
                BEFORE UPDATE ON "toDoList"
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        ''')
        print("✅ Created triggers")
        
        # Verify table exists
        result = await conn.fetchval(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'toDoList'"
        )
        
        if result > 0:
            print("\n" + "=" * 60)
            print("✅ SUCCESS! toDoList table created!")
            print("=" * 60)
            
            # Count rows
            count = await conn.fetchval('SELECT COUNT(*) FROM "toDoList"')
            print(f"\nCurrent rows in table: {count}")
            print("\n✅ You can now use the application!")
        else:
            print("\n❌ Table creation failed")
        
        await conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file has correct PostgreSQL credentials")
        print("   2. Verify you can connect to your AWS RDS instance")
        print("   3. Check security group allows your IP")
        raise

if __name__ == "__main__":
    asyncio.run(create_table())


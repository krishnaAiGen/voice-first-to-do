# AWS RDS PostgreSQL Setup Guide

## Step 1: Get Your AWS RDS Connection Details

You need the following information from your AWS RDS PostgreSQL instance:

1. **Endpoint/Host**: e.g., `mydb.abcdefgh.us-east-1.rds.amazonaws.com`
2. **Port**: Usually `5432` (default PostgreSQL port)
3. **Database Name**: e.g., `todo_voice_db` or `postgres`
4. **Master Username**: e.g., `postgres` or your custom username
5. **Master Password**: The password you set when creating the RDS instance

## Step 2: Update Your .env File

Edit `backend/.env` and update the `DATABASE_URL`:

```bash
# Format
DATABASE_URL=postgresql+asyncpg://USERNAME:PASSWORD@RDS_ENDPOINT:PORT/DATABASE_NAME

# Real Example (replace with your actual values)
DATABASE_URL=postgresql+asyncpg://postgres:MyPassword123@mydb.c9a8b7d6e5f4.us-east-1.rds.amazonaws.com:5432/todo_voice_db
```

**Important Notes:**
- If your password contains special characters (@, :, /, etc.), you need to URL-encode them
- Use `postgresql+asyncpg://` (not just `postgresql://`)
- Make sure the RDS instance allows connections from your IP

### Password URL Encoding

If your password has special characters, encode them:

| Character | Encoded |
|-----------|---------|
| @         | %40     |
| :         | %3A     |
| /         | %2F     |
| ?         | %3F     |
| #         | %23     |
| [         | %5B     |
| ]         | %5D     |
| Space     | %20     |

**Example:**
- Password: `MyP@ss:word`
- Encoded: `MyP%40ss%3Aword`
- URL: `postgresql+asyncpg://postgres:MyP%40ss%3Aword@endpoint:5432/dbname`

## Step 3: Configure AWS RDS Security Group

Your RDS instance must allow incoming connections:

1. Go to AWS RDS Console
2. Select your database instance
3. Click on the VPC security group
4. Edit inbound rules
5. Add rule:
   - **Type**: PostgreSQL
   - **Protocol**: TCP
   - **Port**: 5432
   - **Source**: 
     - For testing: `0.0.0.0/0` (allow from anywhere) ⚠️ Not recommended for production
     - For production: Your specific IP or VPC CIDR

## Step 4: Initialize Database Schema

You need to run the initialization SQL on your AWS RDS database.

### Option A: Using psql Command Line

```bash
# From your backend directory
psql "postgresql://USERNAME:PASSWORD@RDS_ENDPOINT:5432/DATABASE_NAME" < init_db.sql
```

### Option B: Using pgAdmin or DBeaver

1. Connect to your AWS RDS instance using pgAdmin/DBeaver
2. Open `init_db.sql`
3. Execute the SQL script

### Option C: Using Python Script

Create a file `setup_aws_db.py` in the backend directory:

```python
import asyncio
import asyncpg

async def init_database():
    # Read the SQL file
    with open('init_db.sql', 'r') as f:
        sql = f.read()
    
    # Connect and execute
    conn = await asyncpg.connect(
        'postgresql://USERNAME:PASSWORD@RDS_ENDPOINT:5432/DATABASE_NAME'
    )
    
    try:
        await conn.execute(sql)
        print("✅ Database initialized successfully!")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_database())
```

Run it:
```bash
python setup_aws_db.py
```

## Step 5: Test Connection

Create a test script `test_db.py`:

```python
import asyncio
from app.clients.database_client import DatabaseClient
from app.core.config import settings

async def test_connection():
    try:
        db_client = DatabaseClient()
        async with db_client.async_session_maker() as session:
            result = await session.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL!")
            print(f"Version: {version}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

Run it:
```bash
cd backend
python test_db.py
```

## Step 6: Start the Backend

```bash
cd backend
uvicorn app.main:app --reload
```

If successful, you should see:
```
INFO:     Application startup complete.
```

## Troubleshooting

### Error: "Connection refused"

**Cause**: Security group not allowing connections

**Solution**: 
- Check AWS RDS security group inbound rules
- Ensure PostgreSQL (port 5432) is allowed from your IP

### Error: "Password authentication failed"

**Cause**: Wrong username or password

**Solution**:
- Verify credentials in AWS RDS console
- Check for special characters in password (URL encode them)
- Ensure you're using the master username

### Error: "Database does not exist"

**Cause**: Database name is incorrect

**Solution**:
- Check the actual database name in AWS RDS console
- Try using `postgres` as the database name (default)
- Create the database if it doesn't exist

### Error: "Connection timeout"

**Cause**: RDS instance is not publicly accessible

**Solution**:
1. Go to AWS RDS Console
2. Select your instance
3. Click "Modify"
4. Under "Connectivity", set "Public access" to "Yes"
5. Apply changes (may require restart)

## Production Recommendations

### 1. Use Environment Variables from AWS

Instead of hardcoding in `.env`, use:
- AWS Secrets Manager
- AWS Systems Manager Parameter Store
- Environment variables in your deployment platform

### 2. Use Connection Pooling

The application already uses SQLAlchemy's connection pooling, but you can optimize:

```python
# In database_client.py
self.engine = create_async_engine(
    self.database_url,
    pool_size=20,          # Maximum number of connections
    max_overflow=10,       # Additional connections beyond pool_size
    pool_timeout=30,       # Seconds to wait for connection
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

### 3. Enable SSL/TLS

For production, use SSL:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@endpoint:5432/db?ssl=require
```

### 4. Use Read Replicas (Optional)

For high-traffic applications:
- Use AWS RDS read replicas
- Configure read-only queries to use replica endpoints

## Example Complete .env File

```bash
# AWS RDS PostgreSQL
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@mydb.abc123.us-east-1.rds.amazonaws.com:5432/todo_voice_db

# API Keys
DEEPGRAM_API_KEY=abc123your_deepgram_key
GOOGLE_API_KEY=xyz789your_google_key

# App Settings
SECRET_KEY=your-random-secret-key-here
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
DEFAULT_USER_ID=550e8400-e29b-41d4-a716-446655440000
```

## Quick Checklist

Before starting the backend, ensure:

- [ ] AWS RDS PostgreSQL instance is running
- [ ] Security group allows connections from your IP
- [ ] Database is initialized with `init_db.sql`
- [ ] `.env` file has correct DATABASE_URL
- [ ] `.env` file has API keys (Deepgram, Google)
- [ ] Connection test passes

## Need Help?

Common issues:
1. Security group misconfiguration → Add inbound rule for port 5432
2. Wrong database URL → Double-check endpoint, username, password
3. Database not initialized → Run `init_db.sql`
4. Special characters in password → URL encode them

---

**You're all set!** Once configured, the application will connect to your AWS RDS PostgreSQL instance automatically. 🚀


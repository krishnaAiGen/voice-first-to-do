# Architecture Documentation

## System Architecture

This document provides a deep dive into the architectural decisions and design patterns used in the Voice-First To-Do application.

## Table of Contents

1. [High-Level Architecture](#high-level-architecture)
2. [Core Design Principles](#core-design-principles)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Security Architecture](#security-architecture)
8. [Performance Optimizations](#performance-optimizations)

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ VoiceRecorder│  │  TaskList    │  │   TaskCard   │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                     │
│         │ useVoiceCommands hook                              │
│         └─────────────────┐                                  │
└───────────────────────────┼──────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              API Layer                               │    │
│  │  ┌──────────────┐          ┌──────────────┐        │    │
│  │  │  voice.py    │          │  tasks.py    │        │    │
│  │  │ (PRIMARY)    │          │ (FALLBACK)   │        │    │
│  │  └──────┬───────┘          └──────┬───────┘        │    │
│  └─────────┼──────────────────────────┼───────────────┘    │
│            │                          │                      │
│  ┌─────────▼──────────────────────────▼───────────────┐    │
│  │              Service Layer                          │    │
│  │  ┌──────────────┐  ┌──────────────┐               │    │
│  │  │VoiceService  │  │ TaskService  │               │    │
│  │  └──────┬───────┘  └──────────────┘               │    │
│  │         │                                           │    │
│  │  ┌──────▼───────┐  ┌──────────────┐               │    │
│  │  │IntentService │  │QueryExecutor │               │    │
│  │  └──────┬───────┘  └──────┬───────┘               │    │
│  └─────────┼──────────────────┼───────────────────────┘    │
│            │                  │                              │
│  ┌─────────▼──────────────────▼───────────────┐            │
│  │         External Clients & Parsers          │            │
│  │  ┌────────────┐  ┌──────────┐              │            │
│  │  │ Deepgram   │  │ Gemini   │              │            │
│  │  │ (STT)      │  │ (LLM)    │              │            │
│  │  └────────────┘  └────┬─────┘              │            │
│  │                       │                     │            │
│  │  ┌────────────────────▼──────────────┐     │            │
│  │  │      IntentParser                 │     │            │
│  │  └────────────────┬──────────────────┘     │            │
│  └───────────────────┼────────────────────────┘            │
│                      │                                      │
│  ┌───────────────────▼────────────────────────┐            │
│  │      Operations & Query Building           │            │
│  │  ┌────────────┐  ┌──────────────┐         │            │
│  │  │Operations  │  │QueryBuilder  │         │            │
│  │  │(CRUD)      │  │(Safe SQL)    │         │            │
│  │  └────────────┘  └──────┬───────┘         │            │
│  └─────────────────────────┼─────────────────┘            │
│                            │                                │
│  ┌─────────────────────────▼─────────────────┐            │
│  │         Repository Layer                   │            │
│  │  ┌──────────────────────────────┐         │            │
│  │  │     TaskRepository           │         │            │
│  │  └──────────────┬───────────────┘         │            │
│  └─────────────────┼───────────────────────────           │
└────────────────────┼──────────────────────────────────────┘
                     │ asyncpg
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  tasks table                                          │   │
│  │  - Full-text search (tsvector)                        │   │
│  │  - Indexes for performance                            │   │
│  │  - Constraints for data integrity                     │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Specification-Based Architecture

**Why?** Direct SQL generation by LLMs is dangerous and unreliable.

**How?** The LLM generates a JSON specification, not SQL:

```python
{
  "complexity": "simple",
  "steps": [{
    "operation": "create",
    "params": {"title": "Buy groceries", "priority": 2}
  }],
  "natural_response": "Created task 'Buy groceries'"
}
```

Your code then:
1. Validates the specification
2. Builds safe, parameterized SQL
3. Executes with proper error handling

### 2. Layered Architecture

Each layer has a single responsibility:

- **API Layer**: HTTP routing and request/response handling
- **Service Layer**: Business logic orchestration
- **Repository Layer**: Data access and persistence
- **Model Layer**: Domain objects and validation

### 3. Dependency Injection

All dependencies are injected, making the code:
- Testable (can mock dependencies)
- Flexible (easy to swap implementations)
- Clear (explicit dependencies)

## Backend Architecture

### Three-Tier Query System

#### Tier 1: Simple CRUD (90% of queries) - <1.5s

Single operation with 0-2 simple filters.

**Examples**:
- "Create task X"
- "Show high priority tasks"
- "Delete task 5"

**Flow**:
```
User Command → LLM → Single-step spec → Execute → Response
```

#### Tier 2: Multi-Step Sequential (9% of queries) - <2s

Multiple operations planned upfront.

**Examples**:
- "Show overdue tasks and mark top 3 as high priority"

**Flow**:
```
User Command → LLM → Multi-step spec → Execute sequentially → Response
```

#### Tier 3: Interactive Tool Use (1% of queries) - 2-4s

Requires seeing intermediate results.

**Examples**:
- "Find related tasks and create a summary"

**Flow**:
```
User Command → LLM → Step 1 → Execute → LLM → Step 2 → Execute → Response
```

### Service Layer Design

#### VoiceService (Orchestrator)

```python
class VoiceService:
    async def process_command(audio, user_id):
        # 1. Speech to Text
        transcript = await deepgram.transcribe(audio)
        
        # 2. Parse Intent
        intent = await intent_service.parse(transcript)
        
        # 3. Execute
        result = await query_executor.execute(intent.spec)
        
        return result
```

#### QueryExecutor (Execution Engine)

```python
class QueryExecutor:
    async def execute(specification, user_id):
        if specification.complexity == "simple":
            return await self._execute_simple(specification)
        elif specification.complexity == "multi_step":
            return await self._execute_sequential(specification)
        else:
            return await self._execute_interactive(specification)
```

### Safe Query Building

#### FilterBuilder (Whitelist Pattern)

```python
ALLOWED_FILTERS = {
    'is_overdue': lambda q: q.where(
        and_(
            Task.scheduled_time < datetime.now(),
            Task.status != 'completed'
        )
    ),
    'priority_min': lambda q, val: q.where(Task.priority >= val),
    # ... more filters
}
```

**Why Whitelist?**
- Zero SQL injection risk
- Predictable behavior
- Easy to audit
- Testable

## Frontend Architecture

### Component Hierarchy

```
App (page.tsx)
├── VoiceRecorder
│   └── useVoiceCommands hook
│       ├── MediaRecorder API
│       └── API client
└── TaskList
    ├── useTasks hook
    │   └── API client
    └── TaskCard (multiple)
```

### State Management

**Local State** (useState):
- Recording state
- Processing state
- UI state

**Server State** (custom hooks):
- Tasks list (useTasks)
- Voice command results (useVoiceCommands)

### Hooks Architecture

#### useVoiceCommands

Handles the complete voice flow:

```typescript
const {
  isRecording,      // UI state
  isProcessing,     // Loading state
  transcript,       // What user said
  response,         // API response
  startRecording,   // Start capture
  stopRecording     // Stop & process
} = useVoiceCommands();
```

#### useTasks

Manages task state:

```typescript
const {
  tasks,            // Current tasks
  loading,          // Initial load state
  refreshTasks,     // Refetch from API
  updateTaskLocally // Optimistic update
} = useTasks();
```

## Data Flow

### Voice Command Flow

```
1. User clicks microphone
   ↓
2. Browser captures audio (MediaRecorder API)
   ↓
3. Audio → Base64 encoding
   ↓
4. POST /api/voice/process {audio_base64}
   ↓
5. Backend: Deepgram transcribes audio
   ↓
6. Backend: Gemini parses intent
   ↓
7. Backend: QueryExecutor executes spec
   ↓
8. Backend: Returns {transcript, result, natural_response}
   ↓
9. Frontend: Display result & refresh tasks
   ↓
10. User sees updated task list
```

### REST API Flow (Fallback)

```
1. Page loads
   ↓
2. useTasks hook fetches: GET /api/tasks
   ↓
3. Display tasks
   ↓
4. Manual update: PUT /api/tasks/{id}
   ↓
5. Optimistic update + API call
   ↓
6. Refresh on success
```

## Design Patterns

### 1. Repository Pattern

**Purpose**: Separate data access from business logic

```python
class TaskRepository:
    async def create(task_data, user_id):
        # Database logic here
        pass
    
    async def get_by_id(task_id, user_id):
        # Database logic here
        pass
```

### 2. Strategy Pattern

**Purpose**: Different operations with same interface

```python
class BaseOperation:
    async def execute(params, user_id):
        pass

class CreateOperation(BaseOperation):
    async def execute(params, user_id):
        # Create logic
        pass

class UpdateOperation(BaseOperation):
    async def execute(params, user_id):
        # Update logic
        pass
```

### 3. Adapter Pattern

**Purpose**: Wrap external APIs

```python
class DeepgramClient:
    async def transcribe(audio):
        # Wraps Deepgram SDK
        pass

class GeminiClient:
    async def generate_intent(prompt):
        # Wraps Google Gemini SDK
        pass
```

### 4. Factory Pattern

**Purpose**: Create operations dynamically

```python
operations = {
    "create": CreateOperation(repo),
    "read": ReadOperation(repo),
    "update": UpdateOperation(repo),
    "delete": DeleteOperation(repo)
}

operation = operations[spec.operation]
result = await operation.execute(params)
```

## Security Architecture

### Input Validation

1. **Pydantic Schemas**: All API inputs validated
2. **Type Checking**: TypeScript on frontend
3. **Whitelisted Filters**: Only allowed filter types
4. **User Scoping**: All queries include user_id

### SQL Injection Prevention

```python
# ❌ NEVER DO THIS
query = f"SELECT * FROM tasks WHERE title = '{user_input}'"

# ✅ ALWAYS DO THIS
query = select(Task).where(Task.title == user_input)
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Whitelist
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Optimizations

### 1. Async I/O Throughout

```python
# All I/O operations are async
async def process_command():
    transcript = await deepgram.transcribe(audio)  # Async
    intent = await gemini.generate(prompt)          # Async
    result = await db.execute(query)                # Async
```

### 2. Database Indexing

```sql
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_scheduled ON tasks(user_id, scheduled_time);
CREATE INDEX idx_tasks_search ON tasks USING GIN(search_vector);
```

### 3. Connection Pooling

```python
engine = create_async_engine(
    database_url,
    pool_pre_ping=True,  # Check connection health
)
```

### 4. Single LLM Call

Most operations require only ONE LLM call:
- Simple queries: 1 call
- Multi-step: 1 call (all steps planned)
- Only interactive queries need multiple calls (rare)

### 5. Optimistic UI Updates

```typescript
// Update UI immediately
updateTaskLocally(newTask);

// Then sync with server
await api.updateTask(id, updates);
```

## Scalability Considerations

### Horizontal Scaling

- **Stateless API**: No server-side sessions
- **Database Pooling**: Connection management
- **Async Workers**: For background jobs

### Caching Strategy (Future)

- Redis for session data
- CDN for static assets
- Query result caching

### Rate Limiting (Production)

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
async def process_voice_command():
    pass
```

## Testing Strategy

### Unit Tests

- Operations: Test each CRUD operation
- Parsers: Test intent parsing
- Builders: Test query building

### Integration Tests

- API endpoints
- Database operations
- External API clients (mocked)

### E2E Tests

- Full voice command flow
- Frontend interactions

## Deployment Architecture

### Docker Composition

```yaml
services:
  postgres:   # Database
  backend:    # FastAPI app
  frontend:   # Next.js app
```

### Environment Configuration

- `.env` files for secrets
- Environment-specific configs
- Vercel/cloud environment variables

## Future Enhancements

1. **WebSocket Support**: Real-time task updates
2. **Multi-user Support**: User authentication
3. **Task Sharing**: Collaborative features
4. **Advanced Queries**: More complex operations
5. **Voice Synthesis**: Text-to-speech responses
6. **Mobile App**: React Native version
7. **Offline Mode**: PWA with service workers
8. **Analytics**: Usage tracking and insights

---

This architecture provides a solid foundation for a production-ready voice-first application while maintaining security, performance, and maintainability.


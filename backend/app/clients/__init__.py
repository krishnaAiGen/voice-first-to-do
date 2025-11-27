"""External API clients"""

from app.clients.deepgram_client import DeepgramClient
from app.clients.gemini_client import GeminiClient
from app.clients.database_client import DatabaseClient, get_db

__all__ = [
    "DeepgramClient",
    "GeminiClient",
    "DatabaseClient",
    "get_db"
]


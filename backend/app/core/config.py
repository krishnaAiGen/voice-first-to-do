"""Application configuration using Pydantic Settings"""

from typing import List, Optional, Any
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Database - can be provided as single URL or individual components
    database_url: Optional[str] = Field(None, alias="DATABASE_URL")
    postgres_host: Optional[str] = None
    postgres_port: Optional[str] = "5432"
    postgres_database: Optional[str] = None
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    
    @model_validator(mode='after')
    def build_database_url_if_needed(self) -> 'Settings':
        """Build DATABASE_URL from individual components if not provided"""
        if self.database_url:
            return self
        
        # Try to build from individual components
        if all([self.postgres_host, self.postgres_database, self.postgres_user, self.postgres_password]):
            self.database_url = (
                f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_database}"
            )
            return self
        
        raise ValueError(
            "Either DATABASE_URL or all postgres_* fields (host, database, user, password) must be provided"
        )
    
    # External APIs
    deepgram_api_key: str = Field(..., alias="DEEPGRAM_API_KEY")
    google_api_key: str = Field(..., alias="GOOGLE_API_KEY")
    
    # Application
    secret_key: str = Field(..., alias="SECRET_KEY")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000",
        alias="CORS_ORIGINS"
    )
    
    # Default user for demo
    default_user_id: str = Field(..., alias="DEFAULT_USER_ID")
    
    # Conversation memory
    conversation_history: int = Field(default=5, alias="CONVERSATION_HISTORY")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


"""
SmartSortierer Pro - Configuration Management
"""
import os
from typing import Optional


class Settings:
    """Application configuration from environment variables"""
    
    # Security
    API_KEY: str = os.getenv("SS_API_KEY", "dev-test-key")
    SECRET_KEY: str = os.getenv("SS_SECRET_KEY", "dev-secret")
    
    # Storage
    STORAGE_ROOT: str = os.getenv("SS_STORAGE_ROOT", "/mnt/nas/smartsortierer")
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("SS_MAX_UPLOAD_SIZE_MB", "100"))
    
    # Database
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "smartsortierer")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "ssuser")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # Qdrant
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "qdrant")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "smartsortierer_docs")
    
    # Ollama
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "ollama")
    OLLAMA_PORT: int = int(os.getenv("OLLAMA_PORT", "11434"))
    OLLAMA_MODEL_CHAT: str = os.getenv("OLLAMA_MODEL_CHAT", "llama3.2:3b")
    OLLAMA_MODEL_EMBED: str = os.getenv("OLLAMA_MODEL_EMBED", "nomic-embed-text")
    
    # Home Assistant
    HA_ENABLED: bool = os.getenv("HA_ENABLED", "false").lower() == "true"
    HA_URL: Optional[str] = os.getenv("HA_URL")
    HA_TOKEN: Optional[str] = os.getenv("HA_TOKEN")
    HA_CONFIRMATION_MODE: bool = os.getenv("HA_CONFIRMATION_MODE", "true").lower() == "true"
    HA_ALLOWED_DOMAINS: str = os.getenv("HA_ALLOWED_DOMAINS", "light,switch,scene")
    
    # Application
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def database_url(self) -> str:
        """Get PostgreSQL connection string"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection string"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    @property
    def ollama_base_url(self) -> str:
        """Get Ollama API base URL"""
        return f"http://{self.OLLAMA_HOST}:{self.OLLAMA_PORT}"


# Singleton instance
settings = Settings()

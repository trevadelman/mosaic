import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "MOSAIC"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Multi-agent Orchestration System for Adaptive Intelligent Collaboration"
    
    # Environment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # API settings
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'mosaic.db'))}"
    )
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Agent settings
    AGENT_MODE: bool = os.getenv("AGENT_MODE", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

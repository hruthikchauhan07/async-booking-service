import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    PROJECT_NAME: str = "System Design Booking API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-default-secret")
    
    # Render provides this single variable
    # If not found, it stays None
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # Fallback variables for local development
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost") 
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "booking_db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        # 1. Use DATABASE_URL if provided by Render
        if self.DATABASE_URL:
            # Ensure it uses the async driver prefix
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        
        # 2. Otherwise, build it from parts (Local/Docker Desktop)
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore" 
    )

settings = Settings()
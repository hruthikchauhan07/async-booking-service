import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "System Design Booking API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    
    # DATABASE VARIABLES (These read from Docker env vars)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost") 
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "booking_db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    # --- THE FIX: KEEP THE NAME 'DATABASE_URL' ---
    @property
    def DATABASE_URL(self) -> str:
        # This builds the correct URL whether you are on Docker or Local
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Configuration to ignore extra .env fields
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore" 
    )

settings = Settings()
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "KOSHA LABS – Worker Identity & Biometric Management API"
    VERSION: str = "2.4.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:postgres@localhost:5432/koshalabs"
    )
    
    # Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "kosha_super_secret_jwt_key_2026_dev")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Biometric Encryption (AES-256)
    BIOMETRIC_ENCRYPTION_KEY: str = os.getenv(
        "BIOMETRIC_ENCRYPTION_KEY", 
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    )
    
    # Calibrated Thresholds
    MATCH_CONFIDENCE_THRESHOLD: float = 0.85
    UNCERTAIN_LOW_THRESHOLD: float = 0.60
    MODEL_VERSION: str = "kosha-siamese-v1.4"
    
    class Config:
        env_file = ".env"

settings = Settings()

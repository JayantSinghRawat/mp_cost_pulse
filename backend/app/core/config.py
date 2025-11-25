from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/mpcostpulse"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "mpcostpulse"
    
    # API Keys
    MAPBOX_ACCESS_TOKEN: str = ""
    ISOCRONE_API_KEY: str = ""
    BIGBASKET_API_KEY: str = ""
    BLINKIT_API_KEY: str = ""
    
    # API Keys for neighborhood data scraping
    OPENWEATHER_API_KEY: str = ""  # For AQI data
    AQICN_TOKEN: str = "demo"  # For AQI data (free tier)
    ZOMATO_API_KEY: str = ""  # For restaurant ratings and delivery
    GOOGLE_PLACES_API_KEY: str = ""  # For amenities and restaurant data
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Scraping
    SCRAPY_DELAY: float = 1.0
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Airflow
    AIRFLOW_HOME: str = "/opt/airflow"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-use-env-variable"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SMTP Configuration for Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "mohantybrajesh4@gmail.com"
    SMTP_PASS: str = "axrbvuubnrsrctso"
    FROM_EMAIL: str = "mohantybrajesh4@gmail.com"
    
    # OTP Configuration
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()


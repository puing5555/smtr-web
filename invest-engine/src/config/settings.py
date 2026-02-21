"""
Configuration settings for the investment engine
"""
import os
from typing import Optional
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./invest_engine.db")
    
    # DART API
    DART_API_KEY: Optional[str] = os.getenv("DART_API_KEY")
    DART_BASE_URL: str = "https://opendart.fss.or.kr/api"
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Timezone and Scheduling
    TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "Asia/Seoul"))
    MORNING_BRIEFING_TIME: str = os.getenv("MORNING_BRIEFING_TIME", "08:30")
    MARKET_CLOSE_TIME: str = os.getenv("MARKET_CLOSE_TIME", "16:00")
    
    # Stock Alerts
    PRICE_ALERT_THRESHOLD: float = float(os.getenv("PRICE_ALERT_THRESHOLD", "3.0"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/invest_engine.log")
    
    # Development
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

# Create global settings instance
settings = Settings()
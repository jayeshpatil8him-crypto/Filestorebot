import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Bot configuration settings"""
    
    # Telegram API
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = os.getenv("DB_NAME", "file_store_bot")
    
    # Admin/Owner
    OWNER_ID = int(os.getenv("OWNER_ID"))
    
    # Logging
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL")) if os.getenv("LOG_CHANNEL") else None
    
    # Default settings
    DEFAULT_DELETE_TIME = int(os.getenv("DEFAULT_DELETE_TIME", 10))
    DEFAULT_BATCH_EXPIRY = int(os.getenv("DEFAULT_BATCH_EXPIRY", 5))
    
    # Rate limiting
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", 60))
    
    # Encryption
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "my-secret-key-32bytes-long!!")
    
    # Bot info
    BOT_USERNAME = None  # Will be set dynamically

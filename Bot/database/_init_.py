from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import Config

class Database:
    """Database connection manager"""
    client = None
    db = None
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        if cls.client is None:
            cls.client = AsyncIOMotorClient(Config.MONGO_URI)
            cls.db = cls.client[Config.DB_NAME]
        return cls.db
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB"""
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.db = None

async def init_db():
    """Initialize database connection"""
    db = await Database.connect()
    
    # Create indexes
    await db.users.create_index("user_id", unique=True)
    await db.files.create_index("unique_id", unique=True)
    await db.files.create_index("file_id")
    await db.links.create_index("token", unique=True)
    await db.links.create_index("expires_at")
    await db.settings.create_index("key", unique=True)
    
    # Initialize default settings
    await db.settings.update_one(
        {"key": "delete_time"},
        {"$setOnInsert": {"value": Config.DEFAULT_DELETE_TIME}},
        upsert=True
    )
    await db.settings.update_one(
        {"key": "batch_expiry"},
        {"$setOnInsert": {"value": Config.DEFAULT_BATCH_EXPIRY}},
        upsert=True
    )
    
    return db

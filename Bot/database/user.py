from datetime import datetime
from bot.database import Database

class UserDB:
    """User database operations"""
    
    @staticmethod
    async def get_collection():
        db = await Database.connect()
        return db.users
    
    @staticmethod
    async def add_user(user_id, username=None, first_name=None, last_name=None):
        """Add or update user"""
        collection = await UserDB.get_collection()
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "last_active": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        await collection.update_one(
            {"user_id": user_id},
            {"$set": user_data},
            upsert=True
        )
    
    @staticmethod
    async def get_user(user_id):
        """Get user by ID"""
        collection = await UserDB.get_collection()
        return await collection.find_one({"user_id": user_id})
    
    @staticmethod
    async def get_all_users():
        """Get all users"""
        collection = await UserDB.get_collection()
        cursor = collection.find({})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def update_last_active(user_id):
        """Update user's last active timestamp"""
        collection = await UserDB.get_collection()
        await collection.update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.utcnow()}}
      )

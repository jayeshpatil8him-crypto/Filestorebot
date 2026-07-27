from datetime import datetime, timedelta
from bot.database import Database

class LinkDB:
    """Link database operations"""
    
    @staticmethod
    async def get_collection():
        db = await Database.connect()
        return db.links
    
    @staticmethod
    async def create_link(token, data, expiry_minutes=5):
        """Create a new link"""
        collection = await LinkDB.get_collection()
        
        link_data = {
            "token": token,
            "data": data,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=expiry_minutes),
            "used": False
        }
        
        await collection.insert_one(link_data)
        return link_data
    
    @staticmethod
    async def get_link(token):
        """Get link by token"""
        collection = await LinkDB.get_collection()
        return await collection.find_one({"token": token})
    
    @staticmethod
    async def mark_used(token):
        """Mark link as used"""
        collection = await LinkDB.get_collection()
        await collection.update_one(
            {"token": token},
            {"$set": {"used": True}}
        )
    
    @staticmethod
    async def delete_link(token):
        """Delete a link"""
        collection = await LinkDB.get_collection()
        await collection.delete_one({"token": token})
    
    @staticmethod
    async def get_all_links():
        """Get all active links"""
        collection = await LinkDB.get_collection()
        cursor = collection.find({"used": False, "expires_at": {"$gt": datetime.utcnow()}})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def delete_expired_links():
        """Delete expired links"""
        collection = await LinkDB.get_collection()
        await collection.delete_many({"expires_at": {"$lt": datetime.utcnow()}})

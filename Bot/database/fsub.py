from bot.database import Database

class FSubDB:
    """Force subscribe database operations"""
    
    @staticmethod
    async def get_collection():
        db = await Database.connect()
        return db.force_sub
    
    @staticmethod
    async def add_channel(channel_id, invite_link=None):
        """Add force subscribe channel"""
        collection = await FSubDB.get_collection()
        
        channel_data = {
            "channel_id": channel_id,
            "invite_link": invite_link,
            "added_at": datetime.utcnow()
        }
        
        await collection.update_one(
            {"channel_id": channel_id},
            {"$set": channel_data},
            upsert=True
        )
    
    @staticmethod
    async def remove_channel(channel_id):
        """Remove force subscribe channel"""
        collection = await FSubDB.get_collection()
        await collection.delete_one({"channel_id": channel_id})
    
    @staticmethod
    async def get_all_channels():
        """Get all force subscribe channels"""
        collection = await FSubDB.get_collection()
        cursor = collection.find({})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def get_channel(channel_id):
        """Get channel by ID"""
        collection = await FSubDB.get_collection()
        return await collection.find_one({"channel_id": channel_id})

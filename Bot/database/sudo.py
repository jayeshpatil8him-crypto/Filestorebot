from bot.database import Database

class SudoDB:
    """Sudo users database operations"""
    
    @staticmethod
    async def get_collection():
        db = await Database.connect()
        return db.sudo
    
    @staticmethod
    async def add_sudo(user_id, added_by):
        """Add sudo user"""
        collection = await SudoDB.get_collection()
        
        sudo_data = {
            "user_id": user_id,
            "added_by": added_by,
            "added_at": datetime.utcnow()
        }
        
        await collection.update_one(
            {"user_id": user_id},
            {"$set": sudo_data},
            upsert=True
        )
    
    @staticmethod
    async def remove_sudo(user_id):
        """Remove sudo user"""
        collection = await SudoDB.get_collection()
        await collection.delete_one({"user_id": user_id})
    
    @staticmethod
    async def get_sudo_list():
        """Get all sudo users"""
        collection = await SudoDB.get_collection()
        cursor = collection.find({})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def is_sudo(user_id):
        """Check if user is sudo"""
        collection = await SudoDB.get_collection()
        result = await collection.find_one({"user_id": user_id})
        return result is not None

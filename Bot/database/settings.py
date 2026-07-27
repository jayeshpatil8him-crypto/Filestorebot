from bot.database import Database

class SettingsDB:
    """Settings database operations"""
    
    @staticmethod
    async def get_collection():
        db = await Database.connect()
        return db.settings
    
    @staticmethod
    async def get_setting(key, default=None):
        """Get a setting value"""
        collection = await SettingsDB.get_collection()
        result = await collection.find_one({"key": key})
        return result["value"] if result else default
    
    @staticmethod
    async def set_setting(key, value):
        """Set a setting value"""
        collection = await SettingsDB.get_collection()
        await collection.update_one(
            {"key": key},
            {"$set": {"value": value}},
            upsert=True
        )

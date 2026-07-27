from datetime import datetime
from bot.database import Database

class FileDB:
    """File database operations"""
    
    @staticmethod
    async def get_collection():
        db = await Database.connect()
        return db.files
    
    @staticmethod
    async def save_file(file_id, unique_id, filename, filesize, uploader, 
                        caption=None, media_type=None):
        """Save file metadata"""
        collection = await FileDB.get_collection()
        
        file_data = {
            "file_id": file_id,
            "unique_id": unique_id,
            "filename": filename,
            "filesize": filesize,
            "uploader": uploader,
            "upload_date": datetime.utcnow(),
            "caption": caption,
            "media_type": media_type
        }
        
        await collection.update_one(
            {"unique_id": unique_id},
            {"$set": file_data},
            upsert=True
        )
        return file_data
    
    @staticmethod
    async def get_file(unique_id):
        """Get file by unique ID"""
        collection = await FileDB.get_collection()
        return await collection.find_one({"unique_id": unique_id})
    
    @staticmethod
    async def get_file_by_id(file_id):
        """Get file by file_id"""
        collection = await FileDB.get_collection()
        return await collection.find_one({"file_id": file_id})
    
    @staticmethod
    async def get_files_in_range(start_id, end_id):
        """Get files between message IDs"""
        collection = await FileDB.get_collection()
        # This assumes files are stored with sequential IDs
        cursor = collection.find({}).sort("_id", 1).skip(start_id - 1).limit(end_id - start_id + 1)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def get_total_files():
        """Get total number of files"""
        collection = await FileDB.get_collection()
        return await collection.count_documents({})

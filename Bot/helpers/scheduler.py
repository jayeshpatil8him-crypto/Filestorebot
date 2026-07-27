from datetime import datetime, timedelta
from bot.database.links import LinkDB
from bot.database.files import FileDB

class SchedulerManager:
    """Scheduler tasks manager"""
    
    @staticmethod
    async def setup(scheduler):
        """Setup scheduled tasks"""
        
        # Delete expired links every hour
        scheduler.add_job(
            SchedulerManager.delete_expired_links,
            'interval',
            hours=1,
            id='delete_expired_links'
        )
        
        # Clean up old files (if needed)
        scheduler.add_job(
            SchedulerManager.cleanup_old_files,
            'interval',
            days=1,
            id='cleanup_old_files'
        )
    
    @staticmethod
    async def delete_expired_links():
        """Delete expired links"""
        await LinkDB.delete_expired_links()
    
    @staticmethod
    async def cleanup_old_files():
        """Cleanup old files (optional)"""
        # Implement if needed
        pass

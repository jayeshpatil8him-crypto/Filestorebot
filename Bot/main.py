import asyncio
import logging
from pyrogram import Client, idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import Config
from bot.database import init_db
from bot.helpers.scheduler import SchedulerManager
from bot.middlewares.auth import AuthMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FileStoreBot:
    """Main bot class"""
    
    def __init__(self):
        self.app = Client(
            "file_store_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="bot/plugins")
        )
        self.scheduler = AsyncIOScheduler()
        
    async def start(self):
        """Start the bot"""
        try:
            # Initialize database
            await init_db()
            logger.info("✅ Database initialized")
            
            # Start bot
            await self.app.start()
            logger.info("✅ Bot started")
            
            # Get bot info
            bot_info = await self.app.get_me()
            Config.BOT_USERNAME = bot_info.username
            logger.info(f"✅ Bot username: @{bot_info.username}")
            
            # Start scheduler
            self.scheduler.start()
            logger.info("✅ Scheduler started")
            
            # Start scheduler tasks
            await SchedulerManager.setup(self.scheduler)
            
            # Idle
            await idle()
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the bot gracefully"""
        logger.info("🔄 Shutting down...")
        self.scheduler.shutdown()
        await self.app.stop()
        logger.info("✅ Bot stopped")

if __name__ == "__main__":
    bot = FileStoreBot()
    asyncio.run(bot.start())

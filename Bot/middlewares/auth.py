from functools import wraps
from pyrogram.enums import ChatType
from bot.config import Config
from bot.database.users import UserDB

class AuthMiddleware:
    """Authentication middleware"""
    
    @staticmethod
    async def check_user(client, message):
        """Check and register user"""
        if not message.from_user:
            return False
        
        user = message.from_user
        
        # Register user if not exists
        await UserDB.add_user(
            user.id,
            user.username,
            user.first_name,
            user.last_name
        )
        
        # Update last active
        await UserDB.update_last_active(user.id)
        
        return True
    
    @staticmethod
    def auth_required(func):
        """Decorator to require authentication"""
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            if not await AuthMiddleware.check_user(client, message):
                await message.reply("❌ Authentication failed. Please try again.")
                return
            return await func(client, message, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def admin_required(func):
        """Decorator to require admin access"""
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            if not message.from_user:
                return
            
            user_id = message.from_user.id
            
            # Check if owner or sudo
            if user_id != Config.OWNER_ID and not await SudoDB.is_sudo(user_id):
                await message.reply("❌ You don't have permission to use this command.")
                return
            
            return await func(client, message, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def owner_required(func):
        """Decorator to require owner access"""
        @wraps(func)
        async def wrapper(client, message, *args, **kwargs):
            if not message.from_user or message.from_user.id != Config.OWNER_ID:
                await message.reply("❌ This command is only available to the bot owner.")
                return
            
            return await func(client, message, *args, **kwargs)
        return wrapper

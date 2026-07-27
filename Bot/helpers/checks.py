from pyrogram.types import User
from bot.config import Config
from bot.database.sudo import SudoDB
from bot.database.fsub import FSubDB

class Checks:
    """Permission and membership checks"""
    
    @staticmethod
    async def is_owner(user_id):
        """Check if user is owner"""
        return user_id == Config.OWNER_ID
    
    @staticmethod
    async def is_sudo(user_id):
        """Check if user is sudo or owner"""
        if await Checks.is_owner(user_id):
            return True
        return await SudoDB.is_sudo(user_id)
    
    @staticmethod
    async def is_admin(user_id):
        """Check if user is admin (owner or sudo)"""
        return await Checks.is_sudo(user_id)
    
    @staticmethod
    async def check_force_sub(client, user_id):
        """Check if user is subscribed to all force channels"""
        channels = await FSubDB.get_all_channels()
        
        if not channels:
            return True, []
        
        not_subscribed = []
        
        for channel in channels:
            try:
                member = await client.get_chat_member(
                    channel["channel_id"], 
                    user_id
                )
                if member.status in ["left", "kicked", "restricted"]:
                    not_subscribed.append(channel)
            except Exception:
                not_subscribed.append(channel)
        
        return len(not_subscribed) == 0, not_subscribed

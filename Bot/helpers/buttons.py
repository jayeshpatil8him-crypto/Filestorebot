from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.database.fsub import FSubDB

class Buttons:
    """Button generators"""
    
    @staticmethod
    async def force_sub_buttons(user_id):
        """Generate force subscribe buttons"""
        channels = await FSubDB.get_all_channels()
        buttons = []
        
        for channel in channels:
            channel_id = channel["channel_id"]
            invite_link = channel.get("invite_link")
            
            if invite_link:
                # Use invite link
                buttons.append([
                    InlineKeyboardButton(
                        f"📢 Join Channel {channel_id}",
                        url=invite_link
                    )
                ])
            else:
                # Use channel username
                try:
                    # Get chat info
                    chat = await client.get_chat(channel_id)
                    if chat.username:
                        buttons.append([
                            InlineKeyboardButton(
                                f"📢 Join {chat.title}",
                                url=f"https://t.me/{chat.username}"
                            )
                        ])
                except:
                    pass
        
        buttons.append([
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_fsub")
        ])
        buttons.append([
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def start_buttons():
        """Generate start menu buttons"""
        buttons = [
            [
                InlineKeyboardButton("📁 Get File", callback_data="get_file"),
                InlineKeyboardButton("ℹ️ About", callback_data="about")
            ],
            [
                InlineKeyboardButton("👤 Profile", callback_data="profile")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    @staticmethod
    def cancel_button():
        """Generate cancel button"""
        buttons = [[
            InlineKeyboardButton("❌ Cancel", callback_data="cancel")
        ]]
        return InlineKeyboardMarkup(buttons)

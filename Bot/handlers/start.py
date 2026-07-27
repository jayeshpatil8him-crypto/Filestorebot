from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.database.users import UserDB
from bot.database.settings import SettingsDB
from bot.helpers.checks import Checks
from bot.helpers.buttons import Buttons
from bot.middlewares.auth import AuthMiddleware

@Client.on_message(filters.command("start") & filters.private)
@AuthMiddleware.auth_required
async def start_command(client, message):
    """Handle /start command"""
    user = message.from_user
    
    # Check force subscription
    is_subscribed, not_subscribed = await Checks.check_force_sub(client, user.id)
    
    if not is_subscribed:
        # Show force subscribe panel
        text = "⚠️ **Join Required**\n\n"
        text += "You need to join the following channels to use this bot:\n\n"
        
        for channel in not_subscribed:
            text += f"• Channel {channel['channel_id']}\n"
        
        text += "\nAfter joining, click Refresh."
        
        buttons = await Buttons.force_sub_buttons(user.id)
        await message.reply(text, reply_markup=buttons)
        return
    
    # Normal start
    text = f"👋 **Welcome {user.first_name}!**\n\n"
    text += "I'm a File Store Bot. I can store and share files permanently.\n\n"
    
    # Check if admin
    if await Checks.is_admin(user.id):
        text += "**Admin Commands:**\n"
        text += "• /batch - Generate batch link\n"
        text += "• /addfsub - Add force subscribe channel\n"
        text += "• /delfsub - Remove force subscribe channel\n"
        text += "• /viewfsub - View force subscribe channels\n"
        text += "• /genlink - Generate invite link\n"
        text += "• /dellink - Delete invite link\n"
        text += "• /viewlinks - View all invite links\n"
        text += "• /deltime - Set auto delete time\n"
        text += "• /addsudo - Add sudo user\n"
        text += "• /delsudo - Remove sudo user\n"
        text += "• /sudolist - View sudo users\n"
        text += "• /broadcast - Broadcast message\n"
    
    await message.reply(text, reply_markup=Buttons.start_buttons())

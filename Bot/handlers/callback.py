from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.database.fsub import FSubDB
from bot.database.links import LinkDB
from bot.helpers.checks import Checks
from bot.helpers.buttons import Buttons

@Client.on_callback_query()
async def handle_callback(client, callback_query: CallbackQuery):
    """Handle all callback queries"""
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if data == "refresh_fsub":
        # Refresh force subscription check
        is_subscribed, not_subscribed = await Checks.check_force_sub(client, user_id)
        
        if is_subscribed:
            await callback_query.message.edit_text(
                "✅ **All channels joined!**\n\n"
                "You can now use the bot."
            )
        else:
            # Update the force subscribe message
            text = "⚠️ **Join Required**\n\n"
            text += "You need to join the following channels:\n\n"
            
            for channel in not_subscribed:
                text += f"• Channel {channel['channel_id']}\n"
            
            text += "\nAfter joining, click Refresh."
            
            buttons = await Buttons.force_sub_buttons(user_id)
            await callback_query.message.edit_text(text, reply_markup=buttons)
            
        await callback_query.answer()
        
    elif data == "close":
        await callback_query.message.delete()
        await callback_query.answer("Closed")
        
    elif data == "about":
        text = "**🤖 About Bot**\n\n"
        text += "This is a File Store Bot that can:\n"
        text += "• Store files permanently\n"
        text += "• Generate batch links\n"
        text += "• Force subscribe users\n"
        text += "• Auto delete files\n\n"
        text += f"**Bot:** @{Config.BOT_USERNAME}\n"
        text += "**Version:** 2.0.0"
        
        await callback_query.message.edit_text(text)
        await callback_query.answer()
        
    elif data == "profile":
        from bot.database.users import UserDB
        user_data = await UserDB.get_user(user_id)
        
        if user_data:
            text = "**👤 User Profile**\n\n"
            text += f"**ID:** `{user_data['user_id']}`\n"
            text += f"**Username:** @{user_data.get('username', 'N/A')}\n"
            text += f"**Name:** {user_data.get('first_name', 'N/A')}\n"
            text += f"**Last Active:** {user_data.get('last_active', 'N/A')}\n"
            text += f"**Joined:** {user_data.get('created_at', 'N/A')}"
            
            await callback_query.message.edit_text(text)
            await callback_query.answer()
        else:
            await callback_query.answer("User not found", show_alert=True)
            
    elif data == "get_file":
        await callback_query.message.edit_text(
            "📁 **Get File**\n\n"
            "Send me a file ID to retrieve it.\n"
            "Example: `file_123456`"
        )
        await callback_query.answer()
        
    elif data == "cancel":
        await callback_query.message.delete()
        await callback_query.answer("Cancelled")
        
    else:
        await callback_query.answer("Unknown action", show_alert=True)

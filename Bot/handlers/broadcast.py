from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.database.users import UserDB
from bot.middlewares.auth import AuthMiddleware
from bot.helpers.utils import Utils
import asyncio

@Client.on_message(filters.command("broadcast") & filters.private)
@AuthMiddleware.owner_required
async def broadcast_command(client, message):
    """Handle broadcast command"""
    if not message.reply_to_message:
        await message.reply("❌ Reply to a message to broadcast.")
        return
    
    # Send initial message
    status_msg = await message.reply("🔄 Starting broadcast...")
    
    # Get all users
    users = await UserDB.get_all_users()
    total = len(users)
    
    if total == 0:
        await status_msg.edit("❌ No users to broadcast to.")
        return
    
    # Broadcast settings
    BATCH_SIZE = 30
    DELAY_BETWEEN_BATCHES = 2
    DELAY_BETWEEN_MESSAGES = 0.5
    
    # Statistics
    success = 0
    blocked = 0
    failed = 0
    
    # Broadcast to users in batches
    for i in range(0, total, BATCH_SIZE):
        batch = users[i:i+BATCH_SIZE]
        
        for user in batch:
            try:
                # Forward the message
                await client.copy_message(
                    chat_id=user['user_id'],
                    from_chat_id=message.chat.id,
                    message_id=message.reply_to_message.id
                )
                success += 1
                
                # Update progress
                if success % 10 == 0:
                    progress = (i + 1) / total * 100
                    await status_msg.edit(
                        f"🔄 **Broadcasting...**\n"
                        f"Progress: {progress:.1f}%\n"
                        f"✅ Success: {success}\n"
                        f"⛔ Blocked: {blocked}\n"
                        f"❌ Failed: {failed}"
                    )
                
            except Exception as e:
                error_str = str(e).lower()
                if "user is deactivated" in error_str or "bot was blocked" in error_str:
                    blocked += 1
                else:
                    failed += 1
                    print(f"Failed to send to {user['user_id']}: {e}")
            
            # Small delay between messages
            await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
        
        # Delay between batches
        await asyncio.sleep(DELAY_BETWEEN_BATCHES)
    
    # Final statistics
    await status_msg.edit(
        f"✅ **Broadcast completed!**\n\n"
        f"📊 Statistics:\n"
        f"• Total users: {total}\n"
        f"• ✅ Success: {success}\n"
        f"• ⛔ Blocked: {blocked}\n"
        f"• ❌ Failed: {failed}"
    )
    
    # Log broadcast
    await Utils.send_log(
        client,
        f"Broadcast completed: {success}/{total} users",
        "info"
    )

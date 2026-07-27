from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.database.files import FileDB
from bot.database.links import LinkDB
from bot.database.settings import SettingsDB
from bot.helpers.encrypt import encryptor
from bot.helpers.utils import Utils
from bot.helpers.checks import Checks
from bot.middlewares.auth import AuthMiddleware

@Client.on_message(filters.command("batch") & filters.private)
@AuthMiddleware.admin_required
async def batch_command(client, message):
    """Generate batch link"""
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.reply("❌ Usage: /batch start_message_id end_message_id")
            return
        
        start_id = int(args[1])
        end_id = int(args[2])
        
        if start_id > end_id:
            await message.reply("❌ Start ID must be less than End ID.")
            return
        
        # Get files in range
        files = await FileDB.get_files_in_range(start_id, end_id)
        
        if not files:
            await message.reply("❌ No files found in this range.")
            return
        
        # Generate batch token
        import json
        from bot.helpers.utils import Utils
        
        token = Utils.generate_token()
        batch_data = {
            "type": "batch",
            "start_id": start_id,
            "end_id": end_id,
            "file_ids": [file['unique_id'] for file in files],
            "generated_by": message.from_user.id
        }
        
        # Store in database
        expiry_minutes = await SettingsDB.get_setting("batch_expiry", Config.DEFAULT_BATCH_EXPIRY)
        await LinkDB.create_link(token, batch_data, expiry_minutes)
        
        # Generate link
        batch_link = f"https://t.me/{Config.BOT_USERNAME}?start=batch_{token}"
        
        await message.reply(
            f"✅ **Batch link generated!**\n\n"
            f"📊 Files: {len(files)}\n"
            f"🔢 Range: {start_id} - {end_id}\n"
            f"⏰ Expires in: {expiry_minutes} minutes\n\n"
            f"🔗 Link: {batch_link}"
        )
        
        await Utils.send_log(
            client,
            f"Batch link generated: {start_id} - {end_id} ({len(files)} files)",
            "admin"
        )
        
    except (IndexError, ValueError) as e:
        await message.reply(f"❌ Error: {str(e)}")

# Handler for batch links in start command
@Client.on_message(filters.command("start") & filters.private)
@AuthMiddleware.auth_required
async def handle_batch_start(client, message):
    """Handle batch link in start command"""
    try:
        args = message.text.split()
        if len(args) == 2:
            param = args[1]
            
            # Check if it's a batch link
            if param.startswith("batch_"):
                token = param[6:]  # Remove 'batch_' prefix
                
                # Get link data
                link_data = await LinkDB.get_link(token)
                
                if not link_data:
                    await message.reply("❌ Invalid or expired link.")
                    return
                
                if link_data.get("used"):
                    await message.reply("❌ This link has already been used.")
                    return
                
                # Check force subscription
                is_subscribed, not_subscribed = await Checks.check_force_sub(client, message.from_user.id)
                
                if not is_subscribed:
                    # Store token for later use
                    # We'll handle this in callback
                    await message.reply(
                        "⚠️ **Join Required**\n\n"
                        "Please join all required channels first.",
                        reply_markup=await Buttons.force_sub_buttons(message.from_user.id)
                    )
                    # Store token in user session (simplified - in production, use better session management)
                    # For now, we'll store it as a global dict (consider using Redis or similar)
                    # This is a simplified approach - in production, use proper session management
                    return
                
                # Send files
                await send_batch_files(client, message, link_data, token)
                
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

async def send_batch_files(client, message, link_data, token):
    """Send batch files to user"""
    try:
        # Mark link as used
        await LinkDB.mark_used(token)
        
        # Get files
        files = link_data['data']['file_ids']
        
        # Progress message
        progress_msg = await message.reply(
            f"📤 **Sending {len(files)} files...**\n"
            "Please wait..."
        )
        
        sent = 0
        for file_id in files:
            try:
                # Get file from database
                file_data = await FileDB.get_file(file_id)
                
                if not file_data:
                    continue
                
                # Send file
                await client.send_cached_media(
                    chat_id=message.chat.id,
                    file_id=file_data['file_id'],
                    caption=file_data.get('caption')
                )
                
                sent += 1
                
                # Update progress every 5 files
                if sent % 5 == 0:
                    await progress_msg.edit_text(
                        f"📤 **Sending files...**\n"
                        f"Progress: {sent}/{len(files)}"
                    )
                
                # Small delay to avoid flooding
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error sending file {file_id}: {e}")
                continue
        
        await progress_msg.edit_text(
            f"✅ **All files sent!**\n\n"
            f"📊 Total: {sent}/{len(files)} files"
        )
        
        # Auto delete after specified time
        delete_time = await SettingsDB.get_setting("delete_time", Config.DEFAULT_DELETE_TIME)
        if delete_time > 0:
            # Schedule deletion (we'll implement this in the delete handler)
            pass
        
    except Exception as e:
        await message.reply(f"❌ Error sending files: {str(e)}")

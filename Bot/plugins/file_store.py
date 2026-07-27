from pyrogram import Client, filters
from pyrogram.types import Message
from bot.database.files import FileDB
from bot.database.users import UserDB
from bot.helpers.utils import Utils
from bot.middlewares.auth import AuthMiddleware
import asyncio

@Client.on_message(filters.private & filters.document | filters.photo | filters.video | filters.audio)
@AuthMiddleware.auth_required
async def store_file(client: Client, message: Message):
    """Store uploaded files"""
    
    # Get file info
    if message.document:
        file_obj = message.document
        media_type = "document"
    elif message.photo:
        file_obj = message.photo
        media_type = "photo"
    elif message.video:
        file_obj = message.video
        media_type = "video"
    elif message.audio:
        file_obj = message.audio
        media_type = "audio"
    else:
        await message.reply("❌ Unsupported file type.")
        return
    
    try:
        # Extract file details
        file_id = file_obj.file_id
        unique_id = file_obj.file_unique_id
        filename = getattr(file_obj, 'file_name', f"{media_type}_{unique_id[:8]}")
        filesize = file_obj.file_size
        caption = message.caption
        
        # Save to database
        await FileDB.save_file(
            file_id=file_id,
            unique_id=unique_id,
            filename=filename,
            filesize=filesize,
            uploader=message.from_user.id,
            caption=caption,
            media_type=media_type
        )
        
        # Get total files count
        total_files = await FileDB.get_total_files()
        
        await message.reply(
            f"✅ **File stored successfully!**\n\n"
            f"📁 **File ID:** `{unique_id}`\n"
            f"📝 **Name:** {filename}\n"
            f"📊 **Size:** {Utils.format_size(filesize)}\n"
            f"📅 **Total Files:** {total_files}\n\n"
            f"Use this ID to retrieve the file."
        )
        
        # Log file upload
        await Utils.send_log(
            client,
            f"New file stored: {filename} by {message.from_user.id}",
            "info"
        )
        
    except Exception as e:
        await message.reply(f"❌ Error storing file: {str(e)}")
        print(f"File storage error: {e}")

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config
from bot.database.sudo import SudoDB
from bot.database.fsub import FSubDB
from bot.database.settings import SettingsDB
from bot.database.links import LinkDB
from bot.helpers.utils import Utils
from bot.middlewares.auth import AuthMiddleware

# --------------------- SUDO COMMANDS ---------------------

@Client.on_message(filters.command("addsudo") & filters.private)
@AuthMiddleware.owner_required
async def add_sudo(client, message):
    """Add sudo user"""
    try:
        user_id = int(message.text.split()[1])
        await SudoDB.add_sudo(user_id, message.from_user.id)
        await message.reply(f"✅ User {user_id} added to sudo users.")
        await Utils.send_log(client, f"Added sudo user: {user_id}", "admin")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /addsudo user_id")

@Client.on_message(filters.command("delsudo") & filters.private)
@AuthMiddleware.owner_required
async def del_sudo(client, message):
    """Remove sudo user"""
    try:
        user_id = int(message.text.split()[1])
        await SudoDB.remove_sudo(user_id)
        await message.reply(f"✅ User {user_id} removed from sudo users.")
        await Utils.send_log(client, f"Removed sudo user: {user_id}", "admin")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /delsudo user_id")

@Client.on_message(filters.command("sudolist") & filters.private)
@AuthMiddleware.admin_required
async def sudo_list(client, message):
    """List sudo users"""
    sudo_users = await SudoDB.get_sudo_list()
    
    if not sudo_users:
        await message.reply("No sudo users.")
        return
    
    text = "**Sudo Users:**\n\n"
    for user in sudo_users:
        text += f"• User ID: `{user['user_id']}`\n"
        text += f"  Added by: `{user['added_by']}`\n"
        text += f"  Added at: {user['added_at']}\n\n"
    
    await message.reply(text)

# --------------------- FORCE SUB COMMANDS ---------------------

@Client.on_message(filters.command("addfsub") & filters.private)
@AuthMiddleware.admin_required
async def add_fsub(client, message):
    """Add force subscribe channel"""
    try:
        args = message.text.split()
        channel_id = int(args[1])
        invite_link = args[2] if len(args) > 2 else None
        
        await FSubDB.add_channel(channel_id, invite_link)
        await message.reply(f"✅ Channel {channel_id} added to force subscribe.")
        await Utils.send_log(client, f"Added force subscribe channel: {channel_id}", "admin")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /addfsub channel_id [invite_link]")

@Client.on_message(filters.command("delfsub") & filters.private)
@AuthMiddleware.admin_required
async def del_fsub(client, message):
    """Remove force subscribe channel"""
    try:
        channel_id = int(message.text.split()[1])
        await FSubDB.remove_channel(channel_id)
        await message.reply(f"✅ Channel {channel_id} removed from force subscribe.")
        await Utils.send_log(client, f"Removed force subscribe channel: {channel_id}", "admin")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /delfsub channel_id")

@Client.on_message(filters.command("viewfsub") & filters.private)
@AuthMiddleware.admin_required
async def view_fsub(client, message):
    """View force subscribe channels"""
    channels = await FSubDB.get_all_channels()
    
    if not channels:
        await message.reply("No force subscribe channels.")
        return
    
    text = "**Force Subscribe Channels:**\n\n"
    for channel in channels:
        text += f"• Channel ID: `{channel['channel_id']}`\n"
        if channel.get('invite_link'):
            text += f"  Invite: {channel['invite_link']}\n"
        text += f"  Added: {channel['added_at']}\n\n"
    
    await message.reply(text)

# --------------------- SETTINGS COMMANDS ---------------------

@Client.on_message(filters.command("deltime") & filters.private)
@AuthMiddleware.admin_required
async def set_delete_time(client, message):
    """Set auto delete time"""
    try:
        minutes = int(message.text.split()[1])
        await SettingsDB.set_setting("delete_time", minutes)
        await message.reply(f"✅ Auto delete time set to {minutes} minutes.")
        await Utils.send_log(client, f"Set delete time to {minutes} minutes", "admin")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /deltime minutes")

# --------------------- INVITE LINK COMMANDS ---------------------

@Client.on_message(filters.command("genlink") & filters.private)
@AuthMiddleware.admin_required
async def generate_invite(client, message):
    """Generate temporary invite link"""
    try:
        channel_id = int(message.text.split()[1])
        
        # Generate token
        token = Utils.generate_token()
        
        # Store in database
        from bot.database.links import LinkDB
        from datetime import datetime, timedelta
        
        link_data = {
            "type": "invite",
            "channel_id": channel_id,
            "generated_by": message.from_user.id
        }
        
        expiry_minutes = await SettingsDB.get_setting("batch_expiry", 5)
        await LinkDB.create_link(token, link_data, expiry_minutes)
        
        invite_link = f"https://t.me/{Config.BOT_USERNAME}?start=invite_{token}"
        await message.reply(f"✅ Invite link generated:\n\n{invite_link}\n\nExpires in {expiry_minutes} minutes.")
        await Utils.send_log(client, f"Generated invite link for channel {channel_id}", "admin")
        
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /genlink channel_id")

@Client.on_message(filters.command("dellink") & filters.private)
@AuthMiddleware.admin_required
async def delete_invite(client, message):
    """Delete invite link"""
    try:
        token = message.text.split()[1]
        await LinkDB.delete_link(token)
        await message.reply(f"✅ Link {token} deleted.")
        await Utils.send_log(client, f"Deleted invite link: {token}", "admin")
    except (IndexError, ValueError):
        await message.reply("❌ Usage: /dellink token")

@Client.on_message(filters.command("viewlinks") & filters.private)
@AuthMiddleware.admin_required
async def view_links(client, message):
    """View all active links"""
    links = await LinkDB.get_all_links()
    
    if not links:
        await message.reply("No active links.")
        return
    
    text = "**Active Links:**\n\n"
    for link in links:
        text += f"• Token: `{link['token']}`\n"
        text += f"  Type: {link['data'].get('type', 'unknown')}\n"
        text += f"  Expires: {link['expires_at']}\n"
        text += f"  Used: {'Yes' if link['used'] else 'No'}\n\n"
    
    await message.reply(text)

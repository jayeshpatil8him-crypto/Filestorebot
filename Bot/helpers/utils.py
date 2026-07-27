import re
import asyncio
from datetime import datetime
from bot.config import Config

class Utils:
    """Utility functions"""
    
    @staticmethod
    def format_size(size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def format_time(seconds):
        """Format time duration"""
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    @staticmethod
    def extract_message_id(link):
        """Extract message ID from link"""
        pattern = r"https://t\.me/[^/]+/(\d+)"
        match = re.search(pattern, link)
        return int(match.group(1)) if match else None
    
    @staticmethod
    async def send_log(client, message, log_type="info"):
        """Send log to log channel"""
        if not Config.LOG_CHANNEL:
            return
        
        try:
            await client.send_message(
                Config.LOG_CHANNEL,
                f"📋 {log_type.upper()}: {message}"
            )
        except Exception as e:
            print(f"Failed to send log: {e}")
    
    @staticmethod
    def generate_token():
        """Generate random token"""
        import secrets
        import string
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

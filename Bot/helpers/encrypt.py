import hashlib
import base64
from cryptography.fernet import Fernet
from bot.config import Config

class Encryptor:
    """Encryption helper"""
    
    def __init__(self):
        # Generate consistent key from config
        key = hashlib.sha256(Config.ENCRYPTION_KEY.encode()).digest()
        self.cipher = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, text):
        """Encrypt text"""
        return self.cipher.encrypt(text.encode()).decode()
    
    def decrypt(self, encrypted_text):
        """Decrypt text"""
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except:
            return None

encryptor = Encryptor()

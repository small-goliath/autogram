"""
Cryptography utilities for encrypting/decrypting sensitive data.
Uses Fernet symmetric encryption for passwords and session data.
"""

from cryptography.fernet import Fernet
from passlib.context import CryptContext
from .config import get_settings


# Password hashing context (for admin passwords)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Used for admin passwords that need to be verified but never decrypted.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_fernet() -> Fernet:
    """
    Get Fernet cipher instance for encryption/decryption.

    Returns:
        Fernet cipher instance
    """
    settings = get_settings()
    key = settings.ENCRYPTION_KEY.encode()
    return Fernet(key)


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data using Fernet.
    Used for Instagram passwords and session data that need to be decrypted later.

    Args:
        data: Plain text data to encrypt

    Returns:
        Encrypted data (base64 encoded)
    """
    fernet = get_fernet()
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt data that was encrypted with encrypt_data.

    Args:
        encrypted_data: Encrypted data (base64 encoded)

    Returns:
        Decrypted plain text data
    """
    fernet = get_fernet()
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key.
    This should be run once and the key stored in .env file.

    Returns:
        Base64 encoded encryption key
    """
    return Fernet.generate_key().decode()


def generate_totp(totp_secret: str) -> str:
    """
    Generate TOTP code from secret.

    Args:
        totp_secret: Base32 encoded TOTP secret

    Returns:
        6-digit TOTP code
    """
    import pyotp

    totp = pyotp.TOTP(totp_secret)
    return totp.now()

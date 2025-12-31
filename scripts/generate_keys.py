"""
Utility script to generate SECRET_KEY and ENCRYPTION_KEY for .env file.
"""

import secrets
from cryptography.fernet import Fernet


def generate_secret_key() -> str:
    """Generate a random SECRET_KEY for JWT."""
    return secrets.token_hex(32)


def generate_encryption_key() -> str:
    """Generate a Fernet ENCRYPTION_KEY."""
    return Fernet.generate_key().decode()


if __name__ == "__main__":
    print("=== Autogram Key Generation ===\n")

    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()

    print("Add these to your .env file:\n")
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print("\nKeep these keys secure and never commit them to version control!")

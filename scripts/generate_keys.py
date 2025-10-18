"""Generate secret keys for .env file."""
import secrets
from cryptography.fernet import Fernet

print("=" * 70)
print("Generated Keys for .env File")
print("=" * 70)
print()
print("Copy these values to your .env file:")
print()
print(f"SECRET_KEY={secrets.token_urlsafe(32)}")
print(f"ENCRYPTION_KEY={Fernet.generate_key().decode()}")
print()
print("=" * 70)

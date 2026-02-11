"""Cryptographic utilities for credential encryption.

Uses Fernet symmetric encryption with key derived from SECRET_KEY via PBKDF2HMAC.
"""

import base64

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from src.config import settings

# Fixed application salt (stored in code, not secret)
# Combined with SECRET_KEY provides unique encryption key
APP_SALT = b"studyhelper-lk-credentials-v1"


class CryptoError(Exception):
    """Exception for cryptographic operation errors."""

    pass


def get_fernet() -> Fernet:
    """Get Fernet instance using SECRET_KEY + PBKDF2.

    Uses PBKDF2HMAC with 1,200,000 iterations (Django 2025 recommendation).
    Source: https://cryptography.io/en/latest/fernet/

    Returns:
        Fernet instance for encryption/decryption.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=APP_SALT,
        iterations=1_200_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode()))
    return Fernet(key)


def encrypt_credential(value: str) -> str:
    """Encrypt a credential string.

    Args:
        value: Plaintext credential to encrypt.

    Returns:
        Encrypted credential as base64 string.

    Raises:
        CryptoError: If encryption fails.
    """
    try:
        fernet = get_fernet()
        return fernet.encrypt(value.encode()).decode()
    except Exception as e:
        raise CryptoError(f"Failed to encrypt credential: {e}") from e


def decrypt_credential(encrypted: str) -> str:
    """Decrypt a credential string.

    Args:
        encrypted: Encrypted credential as base64 string.

    Returns:
        Decrypted plaintext credential.

    Raises:
        CryptoError: If decryption fails (wrong key, corrupted data, etc.).
    """
    try:
        fernet = get_fernet()
        return fernet.decrypt(encrypted.encode()).decode()
    except InvalidToken as e:
        raise CryptoError(
            "Invalid token - credential may be corrupted or key changed"
        ) from e
    except Exception as e:
        raise CryptoError(f"Failed to decrypt credential: {e}") from e

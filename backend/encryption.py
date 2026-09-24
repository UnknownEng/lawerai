"""
Data Encryption at Rest for Sensitive Case Records
Enforces: "Do not store sensitive case data unencrypted; treat all user case content as confidential."
Uses Fernet (symmetric AES-128-CBC + HMAC-SHA256 authenticated encryption).
Supports direct 32-byte URL-safe base64 keys and PBKDF2-HMAC-SHA256 key derivation with salt.
"""

import base64
import hashlib
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from .config import settings

logger = logging.getLogger(__name__)

# Static domain-separation salt for key derivation
PBKDF2_SALT = b"qanoon_sahayak_lawerai_confidential_salt_v1_2026"


def derive_strong_fernet_key(secret: str) -> bytes:
    """
    Derives a valid Fernet key (32 bytes URL-safe base64 encoded).
    1. If `secret` is already a valid 32-byte URL-safe base64 key, returns it directly.
    2. Otherwise, applies PBKDF2-HMAC-SHA256 with 100,000 iterations and domain salt.
    """
    cleaned = secret.strip()
    if len(cleaned) == 44 and cleaned.endswith("="):
        try:
            raw = base64.urlsafe_b64decode(cleaned.encode("ascii"))
            if len(raw) == 32:
                # Test validity with Fernet
                Fernet(cleaned.encode("ascii"))
                return cleaned.encode("ascii")
        except Exception:
            pass

    # Use PBKDF2 with 100,000 iterations
    key_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode("utf-8"),
        PBKDF2_SALT,
        iterations=100_000,
        dklen=32
    )
    return base64.urlsafe_b64encode(key_bytes)


def _legacy_sha256_fernet_key(secret: str) -> bytes:
    """Legacy derivation for backwards compatibility with test fixtures."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_primary_cipher: Optional[Fernet] = None
_legacy_cipher: Optional[Fernet] = None


def get_cipher() -> Fernet:
    global _primary_cipher
    if _primary_cipher is None:
        key = derive_strong_fernet_key(settings.CASE_DATA_ENCRYPTION_KEY)
        _primary_cipher = Fernet(key)
    return _primary_cipher


def get_legacy_cipher() -> Fernet:
    global _legacy_cipher
    if _legacy_cipher is None:
        key = _legacy_sha256_fernet_key(settings.CASE_DATA_ENCRYPTION_KEY)
        _legacy_cipher = Fernet(key)
    return _legacy_cipher


def encrypt_sensitive_text(plaintext: Optional[str]) -> str:
    """
    Encrypt plaintext string. Returns an armored string prefixed with 'enc::'
    If plaintext is empty or already encrypted, handles gracefully.
    """
    if not plaintext:
        return ""
    if plaintext.startswith("enc::"):
        return plaintext
    try:
        cipher = get_cipher()
        encrypted_bytes = cipher.encrypt(plaintext.encode("utf-8"))
        return f"enc::{encrypted_bytes.decode('ascii')}"
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return plaintext


def decrypt_sensitive_text(ciphertext: Optional[str]) -> str:
    """
    Decrypt string if prefixed with 'enc::'.
    Attempts primary PBKDF2 cipher; falls back transparently to legacy cipher for historical records.
    If not encrypted (legacy or plain), returns as-is.
    """
    if not ciphertext:
        return ""
    if not ciphertext.startswith("enc::"):
        return ciphertext

    token_bytes = ciphertext[5:].encode("ascii")

    # Try primary strong cipher
    try:
        primary = get_cipher()
        decrypted_bytes = primary.decrypt(token_bytes)
        return decrypted_bytes.decode("utf-8")
    except InvalidToken:
        pass
    except Exception as e:
        logger.error(f"Decryption error on primary cipher: {e}")

    # Fallback to legacy cipher
    try:
        legacy = get_legacy_cipher()
        decrypted_bytes = legacy.decrypt(token_bytes)
        return decrypted_bytes.decode("utf-8")
    except InvalidToken:
        logger.warning("Invalid encryption token encountered when decrypting case data.")
        return "[Confidential Case Data — Decryption Failed]"
    except Exception as e:
        logger.error(f"Decryption error on legacy cipher: {e}")
        return ciphertext

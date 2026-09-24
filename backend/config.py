"""
Application Configuration for Qanoon Sahayak (LawerAI)
Production-hardened settings with environment validation, secure secrets enforcement,
S3/R2 storage integration, and beta invite gate.
"""

import os
import secrets
import logging
from typing import List, Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)

INSECURE_TEST_KEYS = {
    "qanoon-sahayak-super-secret-jwt-key-2026-pak-law",
    "replace-this-with-a-random-secure-secret-key-in-production",
    "qanoon-sahayak-confidential-encryption-salt-key-2026",
    "replace-this-with-a-32-byte-base64-or-passphrase-key",
    "secret",
    "password",
    "changeme"
}


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "LawerAI / Qanoon Sahayak"
    APP_VERSION: str = "1.0.0-beta"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database: Supports SQLite (dev) or PostgreSQL (prod, e.g. postgresql+asyncpg://...)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./data/qanoon_sahayak.db"
    )

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "qanoon-sahayak-dev-jwt-key-local-only-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Case Data Confidentiality & Encryption at Rest (Fernet AES-128-CBC + HMAC-SHA256)
    CASE_DATA_ENCRYPTION_KEY: str = os.getenv(
        "CASE_DATA_ENCRYPTION_KEY",
        "qanoon-sahayak-dev-encryption-salt-key-local-only-2026"
    )

    # LLM Provider Configuration
    # Options: "auto", "gemini", "claude", "openai", "local"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto").lower()
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Specific Models
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Vector Storage & Corpus
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    CORPUS_DIR: str = os.path.join(DATA_DIR, "legal_corpus")
    VECTOR_STORE_PATH: str = os.path.join(DATA_DIR, "legal_vector_store.json")
    UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploads")

    # File Storage: "local" (default for dev) or "s3" (Cloudflare R2, AWS S3, Supabase)
    STORAGE_BACKEND: str = os.getenv("STORAGE_BACKEND", "local").lower()
    S3_ENDPOINT_URL: Optional[str] = os.getenv("S3_ENDPOINT_URL")
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME")
    S3_ACCESS_KEY_ID: Optional[str] = os.getenv("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: Optional[str] = os.getenv("S3_SECRET_ACCESS_KEY")
    S3_REGION_NAME: str = os.getenv("S3_REGION_NAME", "auto")

    # CORS Allowed Origins (comma-separated string or list)
    ALLOWED_ORIGINS_RAW: str = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,https://lawerai.vercel.app"
    )

    # Beta Access Gate
    BETA_ACCESS_CODE: str = os.getenv("BETA_ACCESS_CODE", "QANOON-BETA-2026")
    REQUIRE_BETA_CODE: bool = os.getenv("REQUIRE_BETA_CODE", "false").lower() in ("true", "1", "yes")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"

    def get_allowed_origins(self) -> List[str]:
        if not self.ALLOWED_ORIGINS_RAW:
            return ["http://localhost:5173"]
        origins = [orig.strip() for orig in self.ALLOWED_ORIGINS_RAW.split(",") if orig.strip()]
        if self.ENVIRONMENT in ["production", "prod", "staging"]:
            # Strictly disallow wildcard in production with credentials
            origins = [o for o in origins if o != "*"]
            if not origins:
                origins = ["https://lawerai.vercel.app"]
        return origins

    def validate_production_secrets(self):
        """Enforces that production deployments cannot boot with insecure or empty secret keys."""
        is_prod = self.ENVIRONMENT in ["production", "prod", "staging"]
        if is_prod:
            if not self.JWT_SECRET_KEY or self.JWT_SECRET_KEY.lower() in INSECURE_TEST_KEYS:
                raise RuntimeError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: "
                    "JWT_SECRET_KEY is empty or using an insecure test value. "
                    "Set a cryptographically strong random secret via the JWT_SECRET_KEY environment variable."
                )
            if not self.CASE_DATA_ENCRYPTION_KEY or self.CASE_DATA_ENCRYPTION_KEY.lower() in INSECURE_TEST_KEYS:
                raise RuntimeError(
                    "CRITICAL SECURITY CONFIGURATION ERROR: "
                    "CASE_DATA_ENCRYPTION_KEY is empty or using an insecure test value. "
                    "Set a valid 32-byte Fernet key via the CASE_DATA_ENCRYPTION_KEY environment variable."
                )
            if self.STORAGE_BACKEND == "s3" and not (self.S3_BUCKET_NAME and self.S3_ACCESS_KEY_ID and self.S3_SECRET_ACCESS_KEY):
                raise RuntimeError(
                    "CRITICAL STORAGE CONFIGURATION ERROR: "
                    "STORAGE_BACKEND is set to 's3' but required S3 credentials (S3_BUCKET_NAME, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY) are missing."
                )


settings = Settings()
settings.validate_production_secrets()

os.makedirs(settings.DATA_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

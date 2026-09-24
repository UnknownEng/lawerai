"""
Rate Limiting Infrastructure using SlowAPI
Protects chat reasoning, file uploads, and authentication endpoints against abuse and DDoS.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from .config import settings

limiter = Limiter(
    key_func=get_remote_address,
    enabled=settings.RATE_LIMIT_ENABLED,
    default_limits=["120/minute"]
)

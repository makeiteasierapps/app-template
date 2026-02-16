"""
Application configuration loaded from environment variables.
"""

import os

from dotenv import load_dotenv

load_dotenv(override=True)


def _bool(val: str | None) -> bool:
    return (val or "").lower() in ("true", "1", "yes")


# Auth
AUTH_ENABLED: bool = _bool(os.getenv("AUTH_ENABLED", "false"))
KRATOS_PUBLIC_URL: str = os.getenv("KRATOS_PUBLIC_URL", "http://localhost:4433")
APP_URL: str = os.getenv("APP_URL", "http://localhost:3000")

# Session cookie
COOKIE_NAME: str = os.getenv("COOKIE_NAME", "session_token")
COOKIE_SECURE: bool = _bool(os.getenv("COOKIE_SECURE", "false"))
COOKIE_HTTPONLY: bool = True
COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")

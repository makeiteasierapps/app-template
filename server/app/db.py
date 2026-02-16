"""
MongoDB async client using Motor.

This module is opt-in. To enable:
1. Uncomment `motor>=3.3.0` in server/requirements.txt
2. Import and use in your routes (see server/app/routes/items.py for examples)

Environment variables (set in .env for local dev, injected by the platform in production):
  MONGO_URI      — MongoDB connection string (default: mongodb://localhost:27017)
  MONGO_USERNAME — MongoDB username (default: empty)
  MONGO_PASSWORD — MongoDB password (default: empty)
"""

import logging
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db = None

DB_NAME = "__PROJECT_NAME__"


def _get_settings():
    load_dotenv(override=True)
    return {
        "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "username": os.getenv("MONGO_USERNAME", ""),
        "password": os.getenv("MONGO_PASSWORD", ""),
    }


def get_db():
    """Get the database instance (lazy-init)."""
    global _client, _db
    if _db is not None:
        return _db

    settings = _get_settings()
    kwargs = {"directConnection": True}
    if settings["username"] and settings["password"]:
        kwargs["username"] = settings["username"]
        kwargs["password"] = settings["password"]
        kwargs["authSource"] = "admin"

    logger.info("Connecting to MongoDB at %s", settings["uri"])
    _client = AsyncIOMotorClient(settings["uri"], **kwargs)
    _db = _client[DB_NAME]
    return _db


def close_db():
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")

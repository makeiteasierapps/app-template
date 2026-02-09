"""
MongoDB async client using Motor.

This module is opt-in. To enable:
1. Uncomment `motor>=3.3.0` in server/requirements.txt
2. Import and use in your routes (see server/app/routes/items.py for examples)
"""

import logging
import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDbClient:
    """Async MongoDB client using Motor."""

    def __init__(self, db_name: str = "__PROJECT_NAME__"):
        self.logger = logging.getLogger(__name__)
        self.mongo_uri = self._load_mongo_uri()
        self.db_name = db_name
        self._client: AsyncIOMotorClient | None = None
        self._db = None
        self._connect()

    def _load_mongo_uri(self) -> str:
        load_dotenv(override=True)
        is_local = os.getenv("LOCAL_DEV", "").lower() == "true"
        uri = os.getenv("MONGO_URI_DEV") if is_local else os.getenv("MONGO_URI")

        if not uri:
            self.logger.error("MongoDB URI not found in environment variables")
            raise ValueError("MONGO_URI or MONGO_URI_DEV must be set")

        self.logger.info(
            "Loaded MongoDB URI for %s environment",
            "development" if is_local else "production",
        )
        return uri

    def _connect(self) -> None:
        if not self._client:
            self.logger.info("Connecting to MongoDB...")
            try:
                self._client = AsyncIOMotorClient(self.mongo_uri)
                self._db = self._client[self.db_name]
                self.logger.info(
                    "Successfully connected to MongoDB database: %s", self.db_name
                )
            except Exception as e:
                self.logger.error("Failed to connect to MongoDB: %s", str(e))
                raise

    @property
    def db(self):
        """Get the database instance."""
        if self._db is None:
            self._connect()
        return self._db

    @property
    def client(self) -> AsyncIOMotorClient:
        """Get the MongoDB client instance."""
        if self._client is None:
            self._connect()
        return self._client

    def close(self) -> None:
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self.logger.info("MongoDB connection closed")


# Singleton instance
_mongo_client: MongoDbClient | None = None


def get_db_client(db_name: str = "__PROJECT_NAME__") -> MongoDbClient:
    """Get or create the MongoDB client singleton."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoDbClient(db_name)
    return _mongo_client


def get_db():
    """FastAPI dependency to get the database."""
    return get_db_client().db

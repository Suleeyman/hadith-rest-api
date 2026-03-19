import logging

from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from src.core.settings import settings

logger = logging.getLogger(__name__)

# logging.getLogger("pymongo.command").setLevel(logging.DEBUG)


class AppDatabase:
    client: MongoClient | None = None
    database: Database | None = None


# Create a new client and connect to the server
client: MongoClient = MongoClient(
    host=settings.mongo_uri,
    server_api=ServerApi(version="1", strict=True, deprecation_errors=True),
)
database = client.get_database(name=settings.mongo_db)
# Send a ping to confirm a successful connection

db = AppDatabase()


def connect_to_mongodb() -> None:
    logger.info("Connecting to MongoDB...")
    db.client = MongoClient(
        host=settings.mongo_uri,
        server_api=ServerApi(version="1", deprecation_errors=True),
    )
    db.database = db.client[settings.mongo_db]

    try:
        db.client.admin.command("ping")
        logger.info("Successfully connected to MongoDB")
    except Exception:
        logger.exception("Failed to connect to MongoDB")


def close_mongodb_connection() -> None:
    if db.client:
        logger.info("Closing MongoDB connection...")
        db.client.close()
        db.client = None
        db.database = None


def get_database() -> Database:
    if db.database is None:
        raise RuntimeError("Database not initialized")
    return db.database

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logger import setup_logger
import traceback

logger = setup_logger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

# Global database instance
db = Database()

async def connect_to_mongo():
    """
    Creates an asynchronous connection to MongoDB and assigns it to the global db object.
    This should be called during FastAPI startup.
    """
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.db = db.client[settings.MONGODB_DB_NAME]
        
        # Verify connection by sending a ping
        await db.db.command("ping")
        logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DB_NAME}")
    except Exception as e:
        logger.error("CRITICAL ERROR: Failed to connect to MongoDB.")
        logger.error(traceback.format_exc())
        raise e

async def close_mongo_connection():
    """
    Closes the asynchronous MongoDB connection.
    This should be called during FastAPI shutdown.
    """
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed gracefully.")

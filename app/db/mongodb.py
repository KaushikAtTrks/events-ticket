from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import get_settings

settings = get_settings()

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.DB_NAME]

    @classmethod
    async def close_database_connection(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            cls.db = None

    @classmethod
    def get_db(cls):
        return cls.db

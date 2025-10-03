import motor.motor_asyncio
from ..core.config import get_settings

settings = get_settings()
motorClient = motor.motor_asyncio.AsyncIOMotorClient

class MongoDB:
    client: motorClient = None
    db = None

    @classmethod
    async def connect_to_database(cls):
        if cls.client is None:
            cls.client = motorClient(settings.MONGODB_URL)
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

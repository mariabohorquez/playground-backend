import os

from beanie import init_beanie
from dotenv import load_dotenv
from models.character import Character
from models.user import User
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    async def initialize_database(self):
        try:
            client = AsyncIOMotorClient(os.environ.get("COSMOS_CONNECTION_STRING"))
            conn = await client.server_info()
            print(f'Connected to MongoDB {conn.get("version")}')
            await init_beanie(
                database=client["playground"], document_models=[Character, User]
            )
            return client
        except Exception as error:
            print(f"Unable to connect to the MongoDB server with error: {error}.")

    class Config:
        env_file = ".env"

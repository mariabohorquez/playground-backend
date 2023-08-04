import os
from pickle import FALSE
from typing import Any, Optional
from beanie import PydanticObjectId, init_beanie
from click import Option

from dotenv import load_dotenv
from pydantic import BaseSettings
from pymongo import ASCENDING, MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

from models.character import CharacterModel

class Settings(BaseSettings):
    DATABASE_URL : Optional[str] = None
    DATABASE_NAME : Optional[str] = None

    async def initialize_database(self):
        try:
          client = AsyncIOMotorClient(self.DATABASE_URL)
          conn = await client.server_info()
          print(conn)
          print(f'Connected to MongoDB {conn.get("version")}')
          await init_beanie(
              database=client[self.DATABASE_NAME],
              document_models=[CharacterModel]
          )
          return client
        except Exception as error:
            print(error)
            print("Unable to connect to the MongoDB server.")

    class Config:
        env_file = ".env"


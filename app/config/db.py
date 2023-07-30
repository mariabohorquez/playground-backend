import os

from dotenv import load_dotenv
from fastapi.logger import logger
from pymongo import MongoClient

load_dotenv()
CONNECTION_STRING = os.environ.get("COSMOS_CONNECTION_STRING")
logger.info(f"CONNECTION_STRING: {CONNECTION_STRING}")

client = MongoClient(CONNECTION_STRING)

db = client.fastapi
collection = db["playground"]

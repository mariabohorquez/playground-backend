import os

from dotenv import load_dotenv
from pymongo import ASCENDING, MongoClient

load_dotenv()
CONNECTION_STRING = os.environ.get("COSMOS_CONNECTION_STRING")

client = MongoClient(CONNECTION_STRING)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print("Unable to connect to the MongoDB server.")


db = client["playground"]
User = db["users"]
User.create_index([("email", ASCENDING)], unique=True)

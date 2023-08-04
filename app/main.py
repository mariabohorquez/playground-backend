import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient
from config.db import Settings
from routes import user, auth, character

# from typing import Union
load_dotenv()
app = FastAPI()
settings = Settings()

# routes with prefixes
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(character.router, prefix="/character", tags=["character"])

# events
@app.on_event("startup")
async def startup_db_client():
   client = await settings.initialize_database()
   app.mongodb_client = client
   app.database = client[settings.DATABASE_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
  await app.mongodb_client.close()

# default routes
@app.get("/")
async def read_root():
    return {"Health": "Ok"}


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

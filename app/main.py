import os

from dotenv import load_dotenv
from fastapi import FastAPI
from pymongo import MongoClient
from routes import user, auth, character

# from typing import Union


load_dotenv()
app = FastAPI()

# routes with prefixes
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(character.router, prefix="/character", tags=["character"])

# events
@app.on_event("startup")
def startup_db_client():
    CONNECTION_STRING = os.environ.get("COSMOS_CONNECTION_STRING")
    if not CONNECTION_STRING:
        raise Exception("COSMOS_CONNECTION_STRING environment variable not set")
    app.mongodb_client = MongoClient(CONNECTION_STRING)
    app.database = app.mongodb_client["playground"]


@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()


# default routes
@app.get("/")
async def read_root():
    return {"Health": "Ok"}


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

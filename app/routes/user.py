from bson import ObjectId
from config.db import collection
from fastapi import APIRouter
from models.user import User
from schemas.user import users_serializer

user = APIRouter()


@user.get("/")
async def find_all_users():
    users = users_serializer(collection.find())
    return {"status": "Ok", "data": users}


@user.get("/{id}")
async def get_one_user(id: str):
    user = users_serializer(collection.find({"_id": ObjectId(id)}))
    return {"status": "Ok", "data": user}


@user.post("/")
async def create_user(user: User):
    _id = collection.insert_one(dict(user))
    user = users_serializer(collection.find({"_id": _id.inserted_id}))
    return {"status": "Ok", "data": user}


@user.put("/{id}")
async def update_user(id: str, user: User):
    collection.find_one_and_update({"_id": ObjectId(id)}, {"$set": dict(user)})
    user = users_serializer(collection.find({"_id": ObjectId(id)}))
    return {"status": "Ok", "data": user}


@user.delete("/{id}")
async def delete_user(id: str):
    collection.find_one_and_delete({"_id": ObjectId(id)})
    users_serializer(collection.find())
    return {"status": "Ok", "data": []}

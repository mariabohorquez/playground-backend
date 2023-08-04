from bson.objectid import ObjectId
from fastapi import APIRouter, Depends

import config.oauth2 as oauth2
from config.db import User
from schemas.user import UserResponse, userResponseEntity

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(user_id: str = Depends(oauth2.require_user)):
    user = userResponseEntity(User.find_one({"_id": ObjectId(str(user_id))}))
    return {"status": "success", "user": user}
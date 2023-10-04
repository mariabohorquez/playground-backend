import os
from dotenv import load_dotenv
from typing import Annotated
from beanie import PydanticObjectId
from fastapi.encoders import jsonable_encoder
import config.oauth2 as oauth2
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile, status
from models.character import CharacterResponse
from models.user import UpdateUser, UpdateUserResponse, User, WorldBuildingResponse

import cloudinary
import cloudinary.uploader

from routes import worldbuilding

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)

router = APIRouter()


@router.get("/me", response_model=User)
def get_me(current_user: Annotated[User, Depends(oauth2.get_current_user)]):
    print(current_user.__dict__)
    return current_user

@router.put(
    "/update",
    response_description="Update User Data",
    response_model=UpdateUserResponse,
)
async def update_user(
    userId: Annotated[PydanticObjectId, Form(default=...)],
    name: Annotated[str, Form(default=...)],
    photo: UploadFile = File(default=None),
):
    user = await User.get(userId)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with {userId} not found",
        )

    img_url = ""
    if photo != None:
        print("Photo Value: ", photo.filename)
        try:
            result = cloudinary.uploader.upload(
                photo.file,
                folder="playground",
            )
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error uploading image: {error}",
            )
        img_url = result.get("url")

    update_query = {
        "$set" : {
            "name" : name,
            "photo" : img_url if img_url != "" else user.photo,
        }
    }

    result = await user.update(update_query)
    parsed_user = jsonable_encoder(obj=user, exclude={"world_building", "password", "characters"})
    return UpdateUserResponse(user=parsed_user)

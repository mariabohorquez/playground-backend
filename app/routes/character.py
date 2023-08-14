# Image packages
import os
from typing import Annotated

import cloudinary
import cloudinary.uploader
from beanie import PydanticObjectId
from dotenv import load_dotenv
from fastapi import (APIRouter, Body, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.encoders import jsonable_encoder
from models.character import (Character, CharacterDataResponse,
                              CharacterResponse, DeleteCharacterBody, DeleteCharacterResponse,
                              UpdateCharacter, UserCharactersResponse)
from models.user import User

load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)

router = APIRouter()


@router.post(
    "/create",
    response_description="Create character with picture",
    status_code=status.HTTP_201_CREATED,
)
async def create_character(
    userId: Annotated[PydanticObjectId, Form(default=...)],
    name: Annotated[str, Form(default=...)],
    description: Annotated[str, Form(default=...)],
    traits: Annotated[str, Form(default=...)],
    image: UploadFile = File(default=None)
):
    user = await User.get(userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {userId} not found",
        )

    img_url = ""
    if (image != None):
      try:
        result = cloudinary.uploader.upload(
            image.file,
            folder="playground",
        )
      except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error uploading image: {error}",
        )
      img_url = result.get("url")


    character = Character(
        name=name, description=description, traits=traits.split(","), image=img_url
    )

    char_result = await character.create()

    user.characters.append(char_result)
    await user.save()

    return char_result


@router.get(
    "/{characterId}",
    response_description="Get a character data",
    response_model=CharacterDataResponse,
)
async def get_character(characterId: PydanticObjectId):
    character = await Character.get(characterId)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id {characterId} not found",
        )

    return CharacterDataResponse(data=character)


@router.get(
    "/list/{userId}",
    response_description="Get a list of characters from an account",
    response_model=UserCharactersResponse,
)
async def get_user_chars(userId: PydanticObjectId):
    user = await User.find_one(User.id == userId, fetch_links=True)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {userId} not found",
        )

    chars = []
    for char in user.characters:
        chars.append(jsonable_encoder(char))

    return UserCharactersResponse(chars=chars, status="successful")


@router.put(
    "/{characterId}",
    response_description="Update Character Data",
    response_model=CharacterResponse,
)
async def update_character(
    characterId: PydanticObjectId, payload: UpdateCharacter = Body(...)
):
    character = await Character.get(characterId)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with {characterId} not found",
        )

    req = {k: v for k, v in payload.dict().items() if v is not None}
    update_query = {"$set": {field: value for field, value in req.items()}}

    result = await character.update(update_query)
    response = CharacterResponse.parse_obj(result)
    return response


@router.delete(
    "/{characterId}",
    response_description="Delete a character",
    response_model=DeleteCharacterResponse,
)
async def delete_character(characterId: PydanticObjectId, payload : DeleteCharacterBody):
    userId = payload.userId
    user = await User.get(userId)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {userId} not found",
        )

    character = await Character.get(characterId)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id: {characterId} not found",
        )

    await user.fetch_all_links()

    character = None
    for item in user.characters:
        if item.id == characterId:
            character = item

    if character:
        user.characters.remove(character)
        await character.delete()
        await user.save()
        return DeleteCharacterResponse(id=characterId)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Error in delete character process",
    )

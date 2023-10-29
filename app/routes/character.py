# Image packages
import os
from typing import Annotated
from click import prompt

import cloudinary
import cloudinary.uploader
from beanie import PydanticObjectId
from dotenv import load_dotenv
from fastapi import (APIRouter, Body, Depends, File, Form, HTTPException, UploadFile,
                     status)
from fastapi.encoders import jsonable_encoder
from config import oauth2
from config.template import TRAINING_GENERATOR
from models.character import (Character, CharacterDataResponse,
                              CharacterResponse, DeleteCharacterBody,
                              DeleteCharacterResponse, ExportCharacterLinesResponse, UpdateCharacter, UpdateCharacterLineFavoriteResponse,
                              UserCharactersResponse)
from models.dataset_dialogues import DialogueTraining
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
    image: UploadFile = File(default=None),
):
    user = await User.get(userId)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {userId} not found",
        )

    img_url = ""
    if image != None:
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
        chars.append(jsonable_encoder(obj=char))

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
async def delete_character(characterId: PydanticObjectId, payload: DeleteCharacterBody):
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

@router.post(
    "/favorite",
    response_description="Mark a dialogue line as favorite",
    response_model=UpdateCharacterLineFavoriteResponse
)
async def mark_favorite( 
    current_user: Annotated[User, Depends(oauth2.get_current_user)],
    character_id: str,
    favorite : bool,
    line : str,
    additional_context: str = ""):

    character = await Character.get(character_id)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with {character_id} not found",
        )

    update_query = ""
    if favorite:
        update_query = { "$push" : {"favorite_dialogues" : line} }
    else:
        update_query = {"$pull" : {"favorite_dialogues" : line}}

    await character.update(update_query)

    # Data set store values
    training_prompt = TRAINING_GENERATOR.format(
        game_context = current_user.world_building,
        character_name = character.name,
        character_description = character.description,
        character_traits = character.traits,
        additional_context = additional_context,
    )

    if favorite:
      prompt_hash = hash(training_prompt)
      dataset_row = await DialogueTraining.find_by_hash(prompt_hash)

      if not dataset_row:
          dataset_row = DialogueTraining(prompt=training_prompt, lines=[line])
          await dataset_row.create()
      else:
          await dataset_row.update({"$push" : {"lines" : line}})

    return UpdateCharacterLineFavoriteResponse()


@router.get(
    "/export-dialogues/{userId}",
    response_description="Get a Json File with all dialogues of characters",
    response_model=ExportCharacterLinesResponse,
)
async def export_character_lines(userId : PydanticObjectId):
    user = await User.find_one(User.id == userId, fetch_links=True)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {userId} not found",
        )

    lines = {}
    for char in user.characters:
        if len(char.favorite_dialogues) == 0:
            continue
        lines[char.name] = []
        for line in char.favorite_dialogues:
            lines[char.name].append(line)
            

    return ExportCharacterLinesResponse(status="success", lines=lines)    
    
    
from beanie import PydanticObjectId
from fastapi import APIRouter, Body, HTTPException
from fastapi import Depends, HTTPException, Response, status
from models.character import Character, CharacterResponse, CreateCharacter
from models.user import User

router = APIRouter()


@router.post("/create/{userId}")
async def create_character(userId : PydanticObjectId, payload: CreateCharacter = Body(...)):
    user = await User.get(userId)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    character = Character.parse_obj(payload)
    new_char = await character.create()
    user.characters.append(new_char)
    await user.save() 
    new_character = CharacterResponse.parse_obj(new_char)
    return new_character

@router.get(
    "/{userId}", response_description="Get a list of characters from an account"
)
async def get_user_chars(userId: str):
    return {"status": "success", "characters ": ""}


@router.delete("/{characterId}")
async def delete_character(characterId: str):
    return {"status": "success", "characters ": ""}

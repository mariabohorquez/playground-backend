from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from models.character import CharacterModel


router = APIRouter()

@router.post('/create')
async def create_character(character : CharacterModel = Body(...)):
    new_char = await character.insert()
    return {"status" : "success", "character" : ""}

@router.get('/{userId}', response_description="Get a list of characters from an account")
async def get_user_chars(userId : str):
    return {"status" : "success",
            "characters " : ""}

@router.delete('/{characterId}')
async def delete_character(characterId : str):
    return {"status" : "success",
        "characters " : ""}
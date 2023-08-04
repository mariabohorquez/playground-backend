from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status

from models.character import CharacterModel


router = APIRouter()

@router.post('/create')
async def create_character(character : CharacterModel):
    return {"status" : "success", "character" : ""}

@router.get('/{userId}', description="Get characters from an account")
async def get_user_chars(userId : str):
    return {"status" : "success",
            "characters " : ""}

@router.delete('/{characterId}')
async def delete_character(characterId : str):
    return {"status" : "success",
        "characters " : ""}
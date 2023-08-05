from fastapi import APIRouter, Body
from models.character import Character

router = APIRouter()


@router.post("/create")
async def create_character(character: Character = Body(...)):
    await character.insert()
    return {"status": "success", "character": ""}


@router.get(
    "/{userId}", response_description="Get a list of characters from an account"
)
async def get_user_chars(userId: str):
    return {"status": "success", "characters ": ""}


@router.delete("/{characterId}")
async def delete_character(characterId: str):
    return {"status": "success", "characters ": ""}

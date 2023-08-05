from beanie import PydanticObjectId
from fastapi import APIRouter, Body, HTTPException
from fastapi import HTTPException, status
from models.character import Character, CharacterResponse, CreateCharacter, UpdateCharacter, UserCharactersResponse
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
    "/{userId}", 
    response_description="Get a list of characters from an account",
    response_model=UserCharactersResponse
)
async def get_user_chars(userId : PydanticObjectId):

    user = await User.find_one(User.id == userId, fetch_links=True)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with id {userId} not found"
        )
    
    print(user)

    return UserCharactersResponse(data=user.characters, status="successful")


@router.put(
    "/{characterId}",
    response_description="Update Character Data",
    response_model=CharacterResponse,
)
async def update_character_data(characterId : PydanticObjectId, payload : UpdateCharacter = Body(...)):
    character = await Character.get(characterId)

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character with {characterId} not found"
        )
    
    req = {k: v for k, v in payload.dict().items() if v is not None}
    update_query = {"$set": {
        field: value for field, value in req.items()
    }}

    result = await character.update(update_query)
    response = CharacterResponse.parse_obj(result)
    return response



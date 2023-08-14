from typing import List, Optional

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel

class Character(Document):
    name: Indexed(str, unique=True)
    description: str
    traits: List[str]
    image: Optional[str] = None

    class Settings:
        name = "characters"


class CharacterBase(BaseModel):
    name: str
    description: str
    traits: List[str] = []
    image: Optional[str] = None


class CreateCharacter(CharacterBase):
    class Config:
        schema_extra = {
            "example": {
                "name": "Thanatos",
                "description": "The god of death",
                "traits": ["Darker, Evil"],
                "image": "",
            }
        }


class UpdateCharacter(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    traits: Optional[List[str]] = None
    image: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Thanatos",
                "description": "The god of death",
                "traits": ["Darker, Evil"],
                "image": "",
            }
        }


class CharacterResponse(CharacterBase):
    id: PydanticObjectId
    status: str = "success"


class DeleteCharacterResponse(BaseModel):
    id: PydanticObjectId
    status: str = "success"


class CharacterDataResponse(BaseModel):
    data: Character
    status: str = "success"


class UserCharactersResponse(BaseModel):
    chars: List[dict]
    status: str = "success"

class DeleteCharacterBody(BaseModel):
    userId  : PydanticObjectId
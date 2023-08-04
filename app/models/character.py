from enum import unique
from beanie import Document, Indexed
from pydantic import BaseModel
from typing import List, Optional

class Door(Document):
    name : Indexed(str, unique=True)

class CharacterModel(Document):
    name : Indexed(str, unique=True)
    description : str
    traits : List[str]
    image : Optional[str] = None
    

    class Settings:
        name = "characters"

    class Config:
        schema_extra = {
            "example" : {
                "name" : "Thanatos",
                "description" : "The god of death",
                "traits" : ["Darker, Evil"],
                "image" : ""
            }
        }
        
class UpdateCharacterModel(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None
    traits : Optional[List[str]] = None
    image : Optional[str] = None


  
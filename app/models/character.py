from pydantic import BaseModel
from typing import List, Optional

class CharacterModel(BaseModel):
    name : str
    description : str
    traits : List[str]
    image : Optional[str] = None

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


  
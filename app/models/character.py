from pydantic import BaseModel
from typing import List, Optional

class CharacterModel(BaseModel):
    name : str
    description : str
    traits : List[str]
    image : Optional[str]


class UpdateCharacterModel(BaseModel):
    name : Optional[str]
    description : Optional[str]
    traits : Optional[List[str]]
    image : Optional[str]


  
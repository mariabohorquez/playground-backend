from typing import Dict
from pydantic import BaseModel

from models.user import LoggedUserResponse


class Token(BaseModel):
    access_token: str
    token_type: str
    user : dict


class TokenData(BaseModel):
    username: str | None = None

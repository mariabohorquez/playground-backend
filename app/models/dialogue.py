from typing import Literal
from pydantic import BaseModel


class DialogueResponse(BaseModel):
    data: str
    status_code: int

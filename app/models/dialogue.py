from pydantic import BaseModel


class DialogueResponse(BaseModel):
    lines: list[str]

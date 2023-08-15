from pydantic import BaseModel, Json


class DialogueResponse(BaseModel):
    data: Json
    status_code: int

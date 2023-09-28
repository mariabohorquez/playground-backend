from pydantic import BaseModel


class DialogueResponse(BaseModel):
    lines: list[str]


class Speaker(BaseModel):
    name: str
    id: str


class SpeakersResponse(BaseModel):
    speakers: list[Speaker]


class VoiceResponse(BaseModel):
    url: str


class FinetuningResponse(BaseModel):
    response: str
    status: str

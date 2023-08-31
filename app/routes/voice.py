import os
from typing import Annotated

import config.oauth2 as oauth2
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from models.dialogue import Speaker, SpeakersResponse, VoiceResponse
from models.user import User

router = APIRouter()

load_dotenv()

COQUI_API_KEY = os.environ.get("COQUI_API_KEY")


@router.get("/speakers", response_model=SpeakersResponse)
def get_speakers(current_user: Annotated[User, Depends(oauth2.get_current_user)]):
    url = "https://app.coqui.ai/api/v2/speakers?page=1&per_page=60"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {COQUI_API_KEY}",
    }

    response = requests.get(url, headers=headers)
    return SpeakersResponse(
        speakers=[
            Speaker(name=speaker["name"], id=speaker["id"])
            for speaker in response.json()["result"]
        ]
    )


@router.get("/audio", response_model=VoiceResponse)
def get_audio(
    current_user: Annotated[User, Depends(oauth2.get_current_user)],
    voice_id: str,
    dialogue: str,
    voice_speed: float = 1.2,
):
    url = "https://app.coqui.ai/api/v2/samples/xtts/render/"

    payload = {"voice_id": f"{voice_id}", "text": f"{dialogue}", "speed": {voice_speed}}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {COQUI_API_KEY}",
    }

    response = requests.post(url, json=payload, headers=headers)
    return VoiceResponse(url=response.json()["audio_url"])

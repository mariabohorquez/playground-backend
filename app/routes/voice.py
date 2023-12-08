import os
import shutil
import uuid
from typing import Annotated

import config.oauth2 as oauth2
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from models.dialogue import Speaker, SpeakersResponse, VoiceResponse
from models.user import User

router = APIRouter()

load_dotenv()

ELEVEN_LABS_API_KEY = os.environ.get("ELEVEN_LABS_API_KEY")
AUDIO_DIR = "audio_files"


@router.get("/speakers", response_model=SpeakersResponse)
def get_speakers(current_user: Annotated[User, Depends(oauth2.get_current_user)]):
    url = "https://api.elevenlabs.io/v1/voices"

    headers = {"xi-api-key": f"{ELEVEN_LABS_API_KEY}"}

    response = requests.get(url, headers=headers)
    return SpeakersResponse(
        speakers=[
            Speaker(name=speaker["name"], id=speaker["voice_id"])
            for speaker in response.json()["voices"]
        ]
    )


@router.get("/audio", response_model=VoiceResponse)
def get_audio(
    current_user: Annotated[User, Depends(oauth2.get_current_user)],
    voice_id: str,
    dialogue: str,
):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    payload = {
        "model_id": "eleven_multilingual_v2",
        "text": f"{dialogue}",
        "voice_settings": {"similarity_boost": 0.75, "stability": 0.40},
    }
    headers = {
        "xi-api-key": f"{ELEVEN_LABS_API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers)

    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)

    file_path = f"{AUDIO_DIR}/{uuid.uuid4()}.mp3"  # Change 'output.mp3' to a unique name if needed
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=128):
            if chunk:
                f.write(chunk)

    return VoiceResponse(url=file_path)


@router.delete("/audio")
def delete_audio(current_user: Annotated[User, Depends(oauth2.get_current_user)]):
    try:
        # Check if directory exists
        if os.path.exists(AUDIO_DIR):
            # Remove all files in the directory
            for filename in os.listdir(AUDIO_DIR):
                file_path = os.path.join(AUDIO_DIR, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            return {"message": "All audio files deleted successfully."}
        else:
            return {"message": "Audio directory not found."}
    except Exception as e:
        return {"message": f"Error deleting audio files: {e}"}

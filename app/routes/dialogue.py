import os
from typing import Annotated

import openai
from config import oauth2
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, status
from models.dialogue import DialogueResponse
from models.user import User

router = APIRouter()

load_dotenv()

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")


def get_openai_response(current_user):
    openai.api_key = OPENAI_KEY
    return openai.Model.list()


@router.get("/generate", response_model=DialogueResponse)
async def generate(
    current_user: Annotated[User, Depends(oauth2.get_current_user)], model: str
):
    if model == "openai":
        response = get_openai_response(current_user)

    if model == "custom":
        # TODO: Implement custom model
        pass

    return DialogueResponse(data=response, status_code=status.HTTP_200_OK)

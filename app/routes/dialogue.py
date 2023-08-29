import os
from typing import Annotated

import openai
from config import oauth2
from config.template import DIALOGUE_GENERATOR
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from models.character import Character
from models.dialogue import DialogueResponse
from models.user import User

router = APIRouter()

load_dotenv()

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY


def get_openai_response(current_user, character, number_of_lines, additional_context):
    prompt = DIALOGUE_GENERATOR.format(
        game_context=current_user.world_building,
        character_name=character.name,
        character_description=character.description,
        additional_context=additional_context,
        character_traits=", ".join(character.traits),
        number_of_lines=number_of_lines,
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.8,
    )
    print(response)
    return response


@router.get("/generate", response_model=DialogueResponse)
async def generate(
    current_user: Annotated[User, Depends(oauth2.get_current_user)],
    model: str,
    character_id: str,
    additional_context: str = "",
    number_of_lines: int = 3,
):
    character = await Character.get(character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with id: {character_id} not found",
        )

    if model == "openai":
        response = get_openai_response(
            current_user,
            character,
            number_of_lines=number_of_lines,
            additional_context="",
        )

    if model == "custom":
        # TODO: Implement custom model
        pass

    return DialogueResponse(
        lines=[
            line
            for line in response.choices[0].message.content.split("\n")
            if line != ""
        ]
    )

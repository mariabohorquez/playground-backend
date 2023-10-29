import os
from typing import Annotated
import regex as re

import openai
import replicate
from config import oauth2
from config.template import DIALOGUE_GENERATOR, FINETUNE_PROMPT, SYSTEM_PROMPT
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from models.character import Character
from models.dialogue import DialogueResponse, FinetuningResponse
from models.user import User

router = APIRouter()

load_dotenv()

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY


def get_openai_lines(prompt: str):

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.8,
    )

    lines = [re.sub(r"[^a-zA-Z0-9 '.]", '', item.strip()) for item in response.choices[0].message.content.split("\n") if item != ""]

    return DialogueResponse(
        lines=lines
    )


def get_llama_lines(prompt: str):
    response = replicate.run(
        "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
        input={"prompt": prompt, "system_prompt": SYSTEM_PROMPT, "max_new_tokens": 200},
    )

    response = [item for item in response if item != ""]
    response = "".join(response).split("\n")
    # Llama needs some cleaning up for the response, very difficult to remove via prompt.
    response = [re.sub(r"[^a-zA-Z0-9 '.]", '', item[2:].strip()) for item in response if item != ""]
    response.pop(0) 
    return DialogueResponse(lines=response)


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

    prompt = DIALOGUE_GENERATOR.format(
        game_context=current_user.world_building,
        character_name=character.name,
        character_description=character.description,
        additional_context=additional_context,
        character_traits=", ".join(character.traits),
        number_of_lines=number_of_lines,
    )

    if model == "openai":
        response = get_openai_lines(prompt=prompt)
    elif model == "llama":
        response = get_llama_lines(prompt=prompt)

    return response


def finetune_openai(prompt: str):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.8,
    )
    return response


def finetune_llama(prompt: str):
    response = replicate.run(
        "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
        input={"prompt": prompt, "system_prompt": SYSTEM_PROMPT, "max_new_tokens": 100},
    )
    return response


@router.post("/finetuning", response_model=FinetuningResponse)
async def finetune(
    current_user: Annotated[User, Depends(oauth2.get_current_user)],
    model: str,
    line: str,
    liked: bool,
):
    prompt = FINETUNE_PROMPT.format(
        line=line,
        condition="generate" if liked else "avoid",
    )

    if model == "openai":
        response = finetune_openai(prompt)
    elif model == "llama":
        response = finetune_llama(prompt)

    return FinetuningResponse(
        response=response.choices[0].message.content, status=status.HTTP_200_OK
    )

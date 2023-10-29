import json
import os
from http import HTTPStatus
from typing import Annotated

import openai
from config import oauth2
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from models.training import DialogueTraining
from models.user import User

router = APIRouter()

load_dotenv()

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_KEY


@router.post("/train", description="Uploads training data to OpenAI")
async def train(
    current_user: Annotated[User, Depends(oauth2.get_current_user)],
):
    # Fetch documents and convert to desired format
    jsonl_data = []
    items = await DialogueTraining.find_all().to_list(length=None)

    for item in items:
        prompt = item.prompt
        lines = item.lines

        for line in lines:
            messages = [
                {
                    "role": "system",
                    "content": "You are a RPG designer creating creative lines for NPCs in your game",
                },
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": line},
            ]
            jsonl_data.append({"messages": messages})

    # Write to .jsonl file
    with open("training.jsonl", "w") as outfile:
        for entry in jsonl_data:
            json.dump(entry, outfile)
            outfile.write("\n")

    openai.File.create(file=open("training.jsonl", "rb"), purpose="fine-tune")

    # It costs money to train, so we don't want to do it automatically
    return (
        HTTPStatus.OK,
        "File for training has been uploaded. Manually start the finetuning job from the OpenAI dashboard.",
    )

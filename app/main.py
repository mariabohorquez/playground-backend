import os

from config.db import Settings
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import (auth, character, dialogue, training, user, voice,
                    worldbuilding)

load_dotenv()
settings = Settings()

# FastAPI app
app = FastAPI()
origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost",
    "http://localhost:8080",
    "https://playground.com.ar",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes with prefixes
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(character.router, prefix="/character", tags=["character"])
app.include_router(
    worldbuilding.router, prefix="/worldbuilding", tags=["worldbuilding"]
)
app.include_router(dialogue.router, prefix="/dialogue", tags=["dialogue"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(training.router, prefix="/training", tags=["training"])

# static files
AUDIO_DIR = "audio"

# Create the directory if it doesn't exist
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")


# events
@app.on_event("startup")
async def startup_db_client():
    client = await settings.initialize_database()
    app.mongodb_client = client


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


# default routes
@app.get("/")
async def read_root():
    return {"Health": "Ok"}

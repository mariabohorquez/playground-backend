from config.db import Settings
from dotenv import load_dotenv
from fastapi import FastAPI
from routes import auth, character, user

load_dotenv()
settings = Settings()

# FastAPI app
app = FastAPI()

# routes with prefixes
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(character.router, prefix="/character", tags=["character"])


# events
@app.on_event("startup")
async def startup_db_client():
    client = await settings.initialize_database()
    app.mongodb_client = client


@app.on_event("shutdown")
async def shutdown_db_client():
    # await app.mongodb_client.close()
    pass


# default routes
@app.get("/")
async def read_root():
    return {"Health": "Ok"}

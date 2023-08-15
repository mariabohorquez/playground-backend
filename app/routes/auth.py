from datetime import timedelta
from typing import Annotated

from config.oauth2 import create_access_token
from config.utils import hash_password, verify_password
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from models.token import Token
from models.user import CreateUser, User, UserResponse

ACCESS_TOKEN_EXPIRE_MINUTES = 3600


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(payload: CreateUser):
    # Check if user already exist
    user = await User.find_one({"email": payload.email.lower()})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    #  Hash the password
    payload.password = hash_password(payload.password)
    payload.email = payload.email.lower()
    result = await User.parse_obj(payload).create()
    new_user = UserResponse.parse_obj(result)
    return new_user


@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Check if the user exist
    db_user = await User.by_email(form_data.username.lower())
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )

    # Create access token
    user = jsonable_encoder(db_user, exclude={"password"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer", user=user)


@router.get("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
):
    response.set_cookie("logged_in", "", -1)
    return {"status": "success"}

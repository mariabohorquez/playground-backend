from datetime import datetime, timedelta

from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status

import config.oauth2 as oauth2
from config.db import User
from config.oauth2 import AuthJWT
from config.utils import hash_password, verify_password
from schemas.user import (CreateUserSchema, LoginUserSchema, UserResponse,
                              userEntity, userResponseEntity)

router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = 15
REFRESH_TOKEN_EXPIRES_IN = 60


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def create_user(payload: CreateUserSchema):
    # Check if user already exist
    user = User.find_one({"email": payload.email.lower()})
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )
    #  Hash the password
    payload.password = hash_password(payload.password)
    del payload.passwordConfirm
    payload.verified = True
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    payload.updated_at = payload.created_at
    result = User.insert_one(payload.dict())
    new_user = userResponseEntity(User.find_one({"_id": result.inserted_id}))
    return {"status": "success", "user": new_user}


@router.post("/login")
def login(payload: LoginUserSchema, response: Response, Authorize: AuthJWT = Depends()):
    # Check if the user exist
    db_user = User.find_one({"email": payload.email.lower()})
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )
    user = userEntity(db_user)

    # Check if the password is valid
    if not verify_password(payload.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Email or Password",
        )

    # Create access token
    access_token = Authorize.create_access_token(
        subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    )

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(user["id"]),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
    )

    # Store refresh and access tokens in cookie
    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )

    # Send both access
    return {"status": "success", "access_token": access_token}


@router.get("/refresh")
def refresh_token(response: Response, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh access token",
            )
        user = userEntity(User.find_one({"_id": ObjectId(str(user_id))}))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user belonging to this token no logger exist",
            )
        access_token = Authorize.create_access_token(
            subject=str(user["id"]),
            expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
        )
    except Exception as e:
        error = e.__class__.__name__
        if error == "MissingTokenError":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide refresh token",
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )
    return {"access_token": access_token}


@router.get("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    Authorize: AuthJWT = Depends(),
    user_id: str = Depends(oauth2.require_user),
):
    Authorize.unset_jwt_cookies()
    response.set_cookie("logged_in", "", -1)

    return {"status": "success"}

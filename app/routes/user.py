from typing import Annotated

import config.oauth2 as oauth2
from fastapi import APIRouter, Depends
from models.user import User

router = APIRouter()


@router.get("/me", response_model=User)
def get_me(current_user: Annotated[User, Depends(oauth2.get_current_user)]):
    print(current_user.__dict__)
    return current_user

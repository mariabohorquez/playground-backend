import config.oauth2 as oauth2
from fastapi import APIRouter, Depends
from models.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(user_id: str = Depends(oauth2.require_user)):
    return {"status": "success", "user": "user"}

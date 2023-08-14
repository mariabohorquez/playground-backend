from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from models.user import UpdateWorldBuilding, User, WorldBuildingResponse

router = APIRouter()


@router.get(
    "/{userId}",
    response_description="Get the current World building",
    response_model=WorldBuildingResponse,
)
async def get_world_building(userId: PydanticObjectId):
    user = await User.get(userId)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {userId} not found",
        )

    return WorldBuildingResponse(worldbuilding=user.world_building)


@router.put(
    "/{userId}",
    response_description="Update the World building",
    status_code=status.HTTP_200_OK,
)
async def update_world_building(userId: PydanticObjectId, payload: UpdateWorldBuilding):
    user = await User.get(userId)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {userId} not found",
        )

    user.world_building = payload.text

    await user.save()

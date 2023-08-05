from typing import Optional

from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, EmailStr, constr


class User(Document):
    "User DB Representation"
    name: str
    email: Indexed(str, unique=True)
    photo: Optional[str]
    password: str

    class Settings:
        name = "users"

    class Config:
        schema_extra = {"example": {"name": "John Doe", "email": "The god of death"}}

    def __str__(self) -> str:
        return self.email

    def __hash__(self) -> int:
        return hash(self.email)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return self.email == other.email
        return False

    @classmethod
    async def by_email(cls, email: str) -> "User":
        """Get a user by email"""
        return await cls.find_one(cls.email == email)


class UserBase(BaseModel):
    name: str
    email: EmailStr
    photo: Optional[str]
    password: str


class CreateUser(UserBase):
    password: constr(min_length=8)
    passwordConfirm: str
    verified: bool = False


class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    photo: Optional[str] = None


class LoginUser(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserResponse(UserBase):
    id: PydanticObjectId
    status: str = "success"

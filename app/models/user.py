from typing import List, Optional
from xmlrpc.client import Boolean, boolean

from beanie import Document, Indexed, Link, PydanticObjectId
from click import Option
from pydantic import BaseModel, EmailStr, constr

from models.character import Character


class User(Document):
    "User DB Representation"
    name: str
    email: Indexed(str, unique=True)
    photo: Optional[str]
    password: str
    characters : Optional[List[Link[Character]]] = []

    class Settings:
        name = "users"

    class Config:
        schema_extra = {
            "example": {
                "name": "John Doe", 
                "email": "john@gmail.com",
                "password" : "argentina12"
        }}

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
    characters : List[Link[Character]] = []
    first_login : bool = False

class CreateUser(UserBase):

    class Config:
      schema_extra = {
          "example": {
              "name": "John Doe", 
              "email": "john@gmail.com",
              "password" : "argentina12"
      }}


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

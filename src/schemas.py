from graphene_sqlalchemy import SQLAlchemyObjectType
from ./src/models import UserInfo, Imc
from pydantic import BaseModel
from datetime import date


class UserInfoBase(BaseModel):
    username: str


class UserCreate(UserInfoBase):
    fullname: str
    password: str


class UserAuthenticate(UserInfoBase):
    password: str


class UserInformation(UserInfoBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class ImcBase(BaseModel):
    imc: str
    username: str
    date: date


class ImcInformation(ImcBase):
    id: int

    class Config:
        orm_mode = True


class UserInfoSchema(SQLAlchemyObjectType):
    class Meta:
        model = UserInfo


class ImcSchema(SQLAlchemyObjectType):
    class Meta:
        model = Imc
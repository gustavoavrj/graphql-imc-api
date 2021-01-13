from graphene_sqlalchemy import SQLAlchemyObjectType
from models import UserInfo, Anime
from pydantic import BaseModel
from datetime import datetime


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


class AnimeBase(BaseModel):
    anime_id: int
    title: str
    url: str
    image_path: str
    airing_status: int
    num_episodes: int
    mpaa_rating: str
    last_scraped_date: datetime
    title_japanese: str
    synopsis: str
    title_english: str


class ImcInformation(AnimeBase):
    id: int


    class Config:
        orm_mode = True


class UserInfoSchema(SQLAlchemyObjectType):
    class Meta:
        model = UserInfo


class AnimeSchema(SQLAlchemyObjectType):
    class Meta:
        model = Anime
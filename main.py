from logging import log, CRITICAL
import bcrypt
import graphene
import uvicorn
from fastapi import FastAPI, HTTPException
from graphene import String
from graphql import GraphQLError
from jwt import PyJWTError
from starlette.graphql import GraphQLApp
from datetime import date
import crud
import models
from app_utils import decode_access_token
from database import db_session, engine
from schemas import AnimeSchema, UserInfoSchema, UserCreate, UserAuthenticate, TokenData, AnimeBase
from fastapi.middleware.cors import CORSMiddleware
import json
import sys
from datetime import timedelta
import redis
import httpx
import pickle


def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            password="",
            db=0,
            socket_timeout=5,
        )
        ping = client.ping()
        if ping is True:
            print("Connected to redis")
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)

client = redis_connect()


def get_routes_from_cache(key: str) -> str:
    """Data from redis."""

    val = client.get(key)
    return val


def set_routes_to_cache(key: str, value: str) -> bool:
    """Data to redis."""

    state = client.setex(key, timedelta(seconds=3600), value=value,)
    return state

def route_optima(query, keyvalue: str) -> dict:

    # First it looks for the data in redis cache
    data = get_routes_from_cache(key=keyvalue)

    # If cache is found then serves the data from cache
    if data is not None:
        data = pickle.loads(data)
        print("got from redis")
        return data

    else:
        # If cache is not found then sends request to the MapBox API
        data = query.all()
        state = set_routes_to_cache(key=keyvalue, value=pickle.dumps(data))

        # This block sets saves the respose to redis and serves it directly
        return data
def route_optima_search(query, title, keyvalue: str) -> dict:

    # First it looks for the data in redis cache
    data = get_routes_from_cache(key=keyvalue)

    # If cache is found then serves the data from cache
    if data is not None:
        data = pickle.loads(data)
        print("got from redis")
        return data

    else:
        # If cache is not found then sends request to the MapBox API
        data = query.filter(models.Anime.title.like('%' + title + '%' )).all()
        state = set_routes_to_cache(key=keyvalue, value=pickle.dumps(data))

        # This block sets saves the respose to redis and serves it directly
        return data












ACCESS_TOKEN_EXPIRE_MINUTES = 30

db = db_session.session_factory()
models.Base.metadata.create_all(bind=engine)



class Query(graphene.ObjectType):
    all_imc = graphene.List(AnimeSchema)
    
    def resolve_all_imc(self, info):
        
        query = AnimeSchema.get_query(info)
        all_imc = query.all()
        return all_imc


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        fullname = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(lambda: UserInfoSchema)

    @staticmethod
    def mutate(root, info, username, password, fullname, ):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = UserInfoSchema(username=username, password=hashed_password, fullname=fullname)
        ok = True
        db_user = crud.get_user_by_username(db, username=username)
        if db_user:
            raise GraphQLError("Username already registered")
        user_info = UserCreate(username=username, password=password, fullname=fullname)
        crud.create_user(db, user_info)
        return CreateUser(user=user, ok=ok)




class AuthenUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()

    @staticmethod
    def mutate(root, info, username, password):
        db_user = crud.get_user_by_username(db, username=username)
        user_authenticate = UserAuthenticate(username=username, password=password)
        if db_user is None:
            raise GraphQLError("Username not existed")
        else:
            is_password_correct = crud.check_username_password(db, user_authenticate)
            if is_password_correct is False:
                raise GraphQLError("Password is not correct")
            else:
                from datetime import timedelta
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                from app_utils import create_access_token
                access_token = create_access_token(
                    data={"sub": username}, expires_delta=access_token_expires)
                return AuthenUser(token=access_token)

class GetAnimeList(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)

    AnimeList = graphene.List(AnimeSchema)

    @staticmethod
    def mutate(root, info, token):
        
        query = AnimeSchema.get_query(info)
        try:
            payload = decode_access_token(data=token)
            username: str = payload.get("sub")
            if username is None:
                raise GraphQLError("Invalid credentials")
            token_data = TokenData(username=username)
        except PyJWTError:
            raise GraphQLError("Invalid credentials")
        user = crud.get_user_by_username(db, username=token_data.username)
        if user is None:
            raise GraphQLError("Invalid credentials")
        AnimeList = route_optima(query,"allanime")

        return GetAnimeList(AnimeList=AnimeList)


class SearchAnime(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        title = graphene.String(required=True)

    AnimeSearch = graphene.List(AnimeSchema)

    @staticmethod
    def mutate(root, info, token, title):
        
        query = AnimeSchema.get_query(info)
        try:
            payload = decode_access_token(data=token)
            username: str = payload.get("sub")
            if username is None:
                raise GraphQLError("Invalid credentials")
            token_data = TokenData(username=username)
        except PyJWTError:
            raise GraphQLError("Invalid credentials")
        user = crud.get_user_by_username(db, username=token_data.username)
        if user is None:
            raise GraphQLError("Invalid credentials")
        AnimeSearch = route_optima_search(query, title, str(title))
        return SearchAnime(AnimeSearch=AnimeSearch)


class MyMutations(graphene.ObjectType):
    user = CreateUser.Field()
    authen_user = AuthenUser.Field()
    get_anime_list = GetAnimeList.Field()
    search_anime = SearchAnime.Field()


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:4200"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query, mutation=MyMutations)))




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

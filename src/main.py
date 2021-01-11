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
from . import crud
from . import models
from app_utils import decode_access_token
from .database import db_session, engine
from .schemas import ImcSchema, UserInfoSchema, UserCreate, UserAuthenticate, TokenData, ImcBase

ACCESS_TOKEN_EXPIRE_MINUTES = 30


db = db_session.session_factory()
models.Base.metadata.create_all(bind=engine)


class Query(graphene.ObjectType):
    all_imc = graphene.List(ImcSchema)
    
    def resolve_all_imc(self, info):
        query = ImcSchema.get_query(info)
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


class CreateNewImc(graphene.Mutation):
    class Arguments:
        imc = graphene.String(required=True)
        token = graphene.String(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, imc, token):
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
        imc = ImcBase(username=username, imc=imc, date=date.today())
        crud.create_new_imc(db=db, imc=imc)
        ok = True
        return CreateNewImc(ok=ok)



class GetImc(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)

    imc_history = graphene.List(ImcSchema)

    @staticmethod
    def mutate(root, info, token):
        query = ImcSchema.get_query(info)
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
        all_imc = query.filter(models.Imc.username == username).all()
        return CreateNewImc(imc_history=all_imc)




class MyMutations(graphene.ObjectType):
    user = CreateUser.Field()
    authen_user = AuthenUser.Field()
    create_new_imc = CreateNewImc.Field()
    get_imc = GetImc.Field()


app = FastAPI()
app.add_route("/graphql", GraphQLApp(schema=graphene.Schema(query=Query, mutation=MyMutations)))



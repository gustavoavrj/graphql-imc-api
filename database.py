from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://wooi58em3zup4aov:mdh45eaf37nttql3@u3r5w4ayhxzdrw87.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/ififatv96npyl02f"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

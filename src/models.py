from sqlalchemy import Column, Integer, String, Date
from ./src/database import Base


class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), unique=True)
    password = Column(String(100))
    fullname = Column(String(50), unique=True)


class Imc(Base):
    __tablename__ = "imc"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25))
    imc = Column(String(10))
    date = Column(Date)

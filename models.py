from sqlalchemy import Column, Integer, String, Date,TIMESTAMP
from database import Base

class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), unique=True)
    password = Column(String(200))
    fullname = Column(String(50), unique=True)


class Anime(Base):
    __tablename__ = "animes"

    anime_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    url = Column(String(100))
    image_path = Column(String(100))
    airing_status = Column(Integer)
    num_episodes = Column(Integer)
    mpaa_rating = Column(String(100))
    last_scraped_date = Column(TIMESTAMP)
    title_japanese = Column(String(100))
    synopsis = Column(String(500))
    title_english = Column(String(100))


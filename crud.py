from sqlalchemy.orm import Session
import models, schemas
import bcrypt
from datetime import date

def get_user_by_username(db: Session, username: str):
    return db.query(models.UserInfo).filter(models.UserInfo.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = models.UserInfo(username=user.username, password=hashed_password, fullname=user.fullname)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def check_username_password(db: Session, user: schemas.UserAuthenticate):
    db_user_info: models.UserInfo = get_user_by_username(db, username=user.username)
    return bcrypt.checkpw(user.password.encode('utf-8'), db_user_info.password.encode('utf-8'))


def create_new_imc(db: Session, imc: schemas.ImcBase):
    db_imc = models.Imc(username=imc.username, imc=imc.imc, date=date.today())
    db.add(db_imc)
    db.commit()
    db.refresh(db_imc)
    return db_imc


def get_all_imcs(db: Session):
    return db.query(models.Imc).all()


def get_imc_by_username(db: Session, username: str):
    return db.query(models.Imc).filter(models.Imc.username == username).first()

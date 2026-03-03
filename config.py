import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "mysql+pymysql://root:DelulU1848$@localhost/base"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

import os

SECRET_KEY = os.urandom(32)

basedir = os.path.abspath(os.path.dirname(__file__))

db_name = "trivia"
db_host = 'localhost:5432'

SQLALCHEMY_DATABASE_URI = "postgres://vari@{}/{}".format(db_host, db_name)
SQLALCHEMY_TRACK_MODIFICATIONS = False
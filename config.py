import os

base_dir = os.path.abspath(os.path.dirname(__file__))
database_file = os.path.join(base_dir, 'stock.sqlite')


class config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + database_file
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

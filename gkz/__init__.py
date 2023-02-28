from flask import Blueprint


gkz_blueprint = Blueprint('gkz', __name__, url_prefix='/api/gkz')

from .gkz_parse import *

from flask import Blueprint


basedata_blueprint = Blueprint('basedata', __name__, url_prefix='/api/basedata')

from .basedata_parse import *

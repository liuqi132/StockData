from flask import Blueprint

limit = Blueprint('limit', __name__, url_prefix='/api/limit')

# 视图函数要和蓝图在同一个文件中
from .limit_up_parse import *

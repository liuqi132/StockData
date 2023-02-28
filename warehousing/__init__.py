from flask import Blueprint

warehousing_blueprint = Blueprint('warehousing', __name__, url_prefix='/api')

# 视图函数要和蓝图在同一个文件中
from .warehousing_parse import *

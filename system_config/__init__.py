from flask import Blueprint

system_blueprint = Blueprint('system_config', __name__, url_prefix='/api/sys')

# 视图函数要和蓝图在同一个文件中
from .system_config import *

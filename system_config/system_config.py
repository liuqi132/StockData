import json
import os

from config import database_file
from exts import db
from models import LimitUp, TransactionDay
from system_config import system_blueprint


@system_blueprint.route('/getStock', methods=['GET'])
def hello_world():  # put application's code here
    tmp_list = TransactionDay.query.all()
    return tmp_list


def test_limit():
    stock_list = LimitUp.query.filter(LimitUp.transaction_day == '2023-02-03').all()
    for stock in stock_list:
        stock_next = TransactionDay.query.filter(TransactionDay.transaction_day == '2023-02-06',
                                                 TransactionDay.stock_code == stock.stock_code).first()
        if stock_next is not None and 0.03 > ((stock_next.price_start - stock.price_end) / stock.price_end) >= 0:
            stock_0210 = TransactionDay.query.filter(TransactionDay.transaction_day == '2023-02-10',
                                                     TransactionDay.stock_code == stock.stock_code).first()
            print(stock.stock_name, (stock_0210.price_end - stock_next.price_end) * 100 / stock_next.price_end)


@system_blueprint.route('/database_init')
def database_init():
    # 必须要到导入models模块
    # db.drop_all()
    db.create_all()
    if os.path.exists(database_file):
        return '数据库文件初始化成功'
    else:
        return '数据库文件初始化失败'

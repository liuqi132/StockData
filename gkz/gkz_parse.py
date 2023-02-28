from sqlalchemy import and_

from models import TransactionDay, StockBaseInfo
from utils.date_util import get_last_days, get_current_day
from . import gkz_blueprint



@gkz_blueprint.route('/api/get_gkz2')
def get_pre_gkz():
    days = 2
    last_two_days = get_last_days('2023-02-13', -days)
    pre_stock_dict = {}
    gkz_stock_dict = {}
    stock_yesterdays = TransactionDay.query.filter(
        and_(TransactionDay.range_increase > 2,
             TransactionDay.range_increase < 6,
             TransactionDay.transaction_day == last_two_days[0]
             )).all()
    for stock_yesterday in stock_yesterdays:
        gkz_stock_dict[stock_yesterday.stock_code] = stock_yesterday.range_increase
    stock_lists = TransactionDay.query.filter(
        and_(TransactionDay.range_increase > 2, TransactionDay.range_increase < 6,
             TransactionDay.transaction_day == last_two_days[1])).all()
    for stock in stock_lists:
        if stock.stock_code not in gkz_stock_dict.keys():
            continue
        if (not stock.stock_code.startswith('sz300') and
            not stock.stock_code.startswith('sz301') and
            not stock.stock_code.startswith('sh688') and
            stock.price_end > stock.price_start) and stock.price_end < 10 and (
                stock.range_increase + gkz_stock_dict[stock.stock_code]) >= 6:
            print(stock.stock_code, stock.stock_name, stock.price_end, gkz_stock_dict[stock.stock_code],
                  stock.range_increase)
            pre_stock_dict[stock.stock_code] = stock.range_increase
    return 'Done'


@gkz_blueprint.route('/api/get_gkz3')
def get_pre_gkz3():
    days = 3
    stock_lists = StockBaseInfo.query.all()
    last_three_days = get_last_days('2023-02-13', -days)
    stock_filter = {}
    for stock in stock_lists:
        three_days_data = TransactionDay.query.filter(TransactionDay.stock_code == stock.stock_code,
                                                      TransactionDay.transaction_day.in_(last_three_days)).all()
        range_increase_list = []
        for every_day_data in three_days_data:
            if not 1 <= every_day_data.range_increase <= 7 or \
                    every_day_data.price_end > 10 or \
                    every_day_data.price_end < 5 or \
                    (every_day_data.price_end - every_day_data.price_start) < 0:
                break
            range_increase_list.append(every_day_data.range_increase)
        if range_increase_list.__len__() == days and 15 > sum(range_increase_list) > 5:
            stock_filter[stock.stock_code] = stock.stock_name
    for key, value in stock_filter.items():
        print(key, value)

    return 'Good'


@gkz_blueprint.route('/api/get_gkz4')
def get_pre_gkz4():
    days = 5
    stock_lists = StockBaseInfo.query.all()
    last_three_days = get_last_days(get_current_day(), -days)
    stock_filter = {}
    for stock in stock_lists:
        three_days_data = TransactionDay.query.filter(TransactionDay.stock_code == stock.stock_code,
                                                      TransactionDay.transaction_day.in_(last_three_days)).all()
        range_increase_list = []
        for every_day_data in three_days_data:
            if every_day_data.price_end > 9 or \
                    every_day_data.price_end < 5 or \
                    (every_day_data.price_end - every_day_data.price_start) < 0:
                break
            range_increase_list.append(every_day_data.range_increase)
        if range_increase_list.__len__() == days and 5 > sum(range_increase_list) > 0:
            stock_filter[stock.stock_code] = stock.stock_name
    for key, value in stock_filter.items():
        print(key, value)

    return 'Good'

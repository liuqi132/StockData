import json
from datetime import datetime, timedelta, time
from sqlite3 import IntegrityError

import requests
from my_fake_useragent import UserAgent
from sqlalchemy import and_

from exts import db
from get_stock_data import get_all_stock, all_stock_list
from models import TransactionDay, BuySale, StockBaseInfo
from warehousing import warehousing_blueprint

date_today = datetime.utcnow().strftime('%Y-%m-%d')
date_yesterday = (datetime.utcnow() + timedelta(days=-1)).strftime('%Y-%m-%d')

ua = UserAgent(family='chrome')
res = ua.random()
today = datetime.utcnow().strftime('%Y-%m-%d')

headers = {"User-Agent": res}  # 伪装请求头
proxies = {'http': '117.242.36.205:42252'}  # 代理ip


@warehousing_blueprint.route('/parseStock')
def parse_stock():
    get_all_stock()
    try:
        print(all_stock_list.__len__())
        db.session.add_all(all_stock_list)
        db.session.commit()
    except IntegrityError:
        raise '唯一键冲突'
    # try:
    #     db.session.execute('delete from t_stock_buy;')
    #     db.session.flush()
    #     db.session.add_all(handle_stock_bs(all_stock_list))
    #     db.session.commit()
    # except Exception as exception:
    #     raise str(exception)
    return '插入完成'


@warehousing_blueprint.route('/delete_buySpot')
def delete_buy_spot():
    db.session.execute('delete from t_stock_buy;')
    db.session.commit()
    return '删除b-s点成功'


@warehousing_blueprint.route('/delete')
def delete_stock():
    try:
        TransactionDay.query.filter(TransactionDay.transaction_day == datetime.utcnow().strftime('%Y-%m-%d')).delete()
        db.session.commit()
    except IntegrityError:
        raise '唯一键冲突'
    return '删除成功'


@warehousing_blueprint.route('/get_history_sh')
def history_data_sh():
    history_data_url = 'http://query.sse.com.cn/commonQuery.do'
    history_data_param = {
        'jsonCallBack': 'jsonpCallback1091099',
        'sqlId': 'COMMON_SSE_CP_GPJCTPZ_GPLB_CJGK_MRGK_C',
        'TX_DATE': date_yesterday,
        'TX_DATE_MON': '',
        'TX_DATE_YEAR': '',
        '_': int(round(time.time() * 1000))
    }
    headers['Referer'] = 'http://www.sse.com.cn/'
    headers['User-Agent'] = 'PostmanRuntime/7.30.0'
    headers['Cookie'] = 'JSESSIONID=DDDD3FAD4CDA0DA8522904FBDB6FB975'
    stock_list_sh = TransactionDay.query.filter_by(transaction_day='2023-02-10').all()
    try:
        for stock_info in stock_list_sh:
            stock_single = TransactionDay.query.filter(and_(
                TransactionDay.transaction_day == '2023-02-13',
                TransactionDay.stock_code == stock_info.stock_code)).first()
            if stock_info.stock_code.startswith('sz') or stock_info.stock_code.startswith(
                    'sh688') or stock_info.stock_code.startswith('sh90'):
                continue
            if stock_single:
                continue
            history_data_param['SEC_CODE'] = stock_info.stock_code.strip('sh')
            history_response = requests.get(url=history_data_url,
                                            params=history_data_param,
                                            headers=headers)
            stock_json = json.loads(history_response.text.split('(')[1].split(')')[0])
            transaction_info = TransactionDay()
            transaction_info.transaction_day = datetime.strptime(date_yesterday, '%Y-%m-%d')
            transaction_info.stock_code = stock_info.stock_code
            transaction_info.stock_name = stock_info.stock_name
            transaction_info.price_yesterday = stock_info.price_end
            transaction_info.price_start = stock_json['result'][0]['OPEN_PRICE']
            transaction_info.price_high = stock_json['result'][0]['HIGH_PRICE']
            transaction_info.price_low = stock_json['result'][0]['LOW_PRICE']
            transaction_info.price_end = stock_json['result'][0]['CLOSE_PRICE']
            transaction_info.range_increase = stock_json['result'][0]['CHANGE_RATE']
            transaction_info.account_business = stock_json['result'][0]['TRADE_VOL']
            transaction_info.cash_business = stock_json['result'][0]['TRADE_AMT']
            db.session.add(transaction_info)
            db.session.flush()
            print(str(transaction_info))
            time.sleep(1.5)
    except Exception as str_exc:
        print('我是异常')
        print(str(str_exc))
        print(history_response.text)
        print(history_response.url)
    finally:
        db.session.commit()
    return f'数据修复完成，修复记录数：'


@warehousing_blueprint.route('/get_buySpot')
def query_buy_spot():
    tmp_list = []
    buy_spots_list = BuySale.query.filter(and_(BuySale.spot_date == '2023-01-12', BuySale.spot_type == 1)).all()
    for buy_spot in buy_spots_list:
        tmp_list.append(buy_spot.stock_code)
    print(tmp_list)
    stock_info_list = TransactionDay.query.filter(and_(TransactionDay.stock_code.in_(tmp_list),
                                                       TransactionDay.transaction_day == date_yesterday)).all()
    for stock_info in stock_info_list:
        if stock_info.price_end < 15:
            print(stock_info.stock_code, stock_info.stock_name)
    return 'Hello world'


@warehousing_blueprint.route('/base_info_load')
def base_info_load():
    stock_tmp_list = []
    all_stocks = TransactionDay.query.filter_by(transaction_day='2023-01-31').all()
    for stock in all_stocks:
        if stock.stock_code.startswith('sz300') or stock.stock_code.startswith('sz301') or stock.stock_code.startswith(
                'sh688'):
            continue
        stock_info = StockBaseInfo(stock_code=stock.stock_code, stock_name=stock.stock_name)
        stock_tmp_list.append(stock_info)
    # db.session.add_all(stock_tmp_list)
    # db.session.commit()
    return '加入成功'

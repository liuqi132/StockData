import json
import math
import os.path
import random
import time
from datetime import datetime, timedelta

import pandas
import requests
from my_fake_useragent import UserAgent

from models import TransactionDay, BuySale

ua = UserAgent(family='chrome')
res = ua.random()
today = datetime.utcnow().strftime('%Y-%m-%d')

headers = {"User-Agent": res}  # 伪装请求头
proxies = {'http': '117.242.36.205:42252'}  # 代理ip

all_stock_dict = {}


class RealTimeInfo_SH:
    def __init__(self, *args):
        self.name = args[0]
        self.prev_close = args[1]
        self.price_start = args[2]
        self.price_high = args[3]
        self.price_low = args[4]
        self.price_current = args[5]
        self.change = args[6]
        self.change_rate = float(args[7])
        self.volume = args[8]
        self.amount = args[9]
        self.cpxxlmttype = args[10]
        self.up_limit = args[11]
        self.down_limit = args[12]

    def __len__(self):
        return len(self.name)


class RealTimeInfo_SZ:
    def __init__(self, **args):
        self.name = args['name']
        self.prev_close = args['close']
        self.price_start = args['open']
        self.price_high = args['high']
        self.price_low = args['low']
        self.price_current = args['now']
        self.change = args['delta']
        self.change_rate = float(args['deltaPercent'])
        self.volume = args['volume']
        self.amount = args['amount']

    def __repr__(self):
        return self.name

    def __len__(self):
        return len(self.name)


def get_stock_shanghai():
    stock_all_list = []
    begin = 0
    end = 500
    stock_url = 'http://yunhq.sse.com.cn:32041/v1/sh1/list/exchange/equity?'
    get_stock_param = {
        'callback': 'jsonpCallback',
        'select': 'code,name,open,high,low,last,prev_close,chg_rate,volume,amount,tradephase,change,amp_rate,'
                  'cpxxsubtype,cpxxprodusta',
        'begin': begin,
        'end': end,
        '_': int(round(time.time() * 1000))
    }
    stock_response = requests.request(method='GET', url=stock_url, params=get_stock_param)
    stock_json = json.loads(stock_response.text.split('(')[1].split(')')[0])
    stock_all_list += stock_json['list']
    total_count = stock_json.get('total')
    for i in range(math.ceil(total_count / 500) - 1):
        begin += 500
        end += 500
        get_stock_param['begin'] = begin
        get_stock_param['end'] = end
        stock_response = requests.request(method='GET', url=stock_url, params=get_stock_param)
        stock_json = json.loads(stock_response.text.split('(')[1].split(')')[0])
        stock_all_list += stock_json['list']
    return stock_all_list


def get_stock_realTime_sh(stock_code: str):
    stock_url = f'http://yunhq.sse.com.cn:32041/v1/sh1/snap/{stock_code}'
    get_stock_param = {
        'callback': 'jsonpCallback',
        'select': 'name,prev_close,open,high,low,last,change,chg_rate,volume,amount,cpxxlmttype,up_limit,down_limit',
        '_': int(round(time.time() * 1000))
    }
    stock_real_time_response = requests.request(method='GET', url=stock_url, params=get_stock_param)
    stock_json = json.loads(stock_real_time_response.text.split('(')[1].split(')')[0])
    stock_real_time_info = stock_json['snap']
    real_time_info = RealTimeInfo_SH(*stock_real_time_info)
    return real_time_info


def get_stock_realTime_sz(stock_code: str):
    stock_url = f'http://www.szse.cn/api/market/ssjjhq/getTimeData'
    get_stock_param = {
        'random': random.random(),
        'marketId': 1,
        'code': stock_code
    }
    stock_real_time_response = requests.request(method='GET', url=stock_url, params=get_stock_param)
    stock_json = json.loads(stock_real_time_response.text)
    stock_real_time_info = stock_json['data']
    real_time_info = RealTimeInfo_SZ(**stock_real_time_info)
    return real_time_info


def get_stock_shenzhen():
    shenzhen_stock_url = 'http://www.szse.cn/api/report/ShowReport/data'
    shenzhen_stock_xlsx = f'http://www.szse.cn/api/report/ShowReport?'
    print(today)
    stock_param = {
        'SHOWTYPE': 'JSON',
        'CATALOGID': '1815_stock',
        'TABKEY': 'tab1',
        'txtBeginDate': today,
        'txtEndDate': today,
        'PAGENO': 1,
    }
    stock_xmls = {
        'SHOWTYPE': 'xlsx',
        'CATALOGID': '1815_stock',
        'TABKEY': 'tab1',
        'txtBeginDate': today,
        'txtEndDate': today
    }
    a_shenzhen_count = 0
    a_shenzhen_list = []
    shenzhen_stock_response = requests.get(url=shenzhen_stock_xlsx, params=stock_xmls)
    time.sleep(2)
    if shenzhen_stock_response.status_code == 200:
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'
        with open(filename, 'wb') as f_stock:
            print(shenzhen_stock_response.content)
            f_stock.write(shenzhen_stock_response.content)
    # for stock_data in shenzhen_stock_response.json():
    #     if stock_data['metadata']['name'] == '股票行情':
    #         a_shenzhen_count = stock_data['metadata']['pagecount']
    #         a_shenzhen_list += stock_data['data']
    # for i in range(2, a_shenzhen_count + 1):
    #     stock_param['PAGENO'] = i
    #     shenzhen_stock_response_next = requests.request(method='GET', url=shenzhen_stock_url, params=stock_param)
    #     print(shenzhen_stock_response_next.text)
    #     for stock_data_next in shenzhen_stock_response_next.json():
    #         if stock_data_next['metadata']['name'] == '股票行情':
    #             a_shenzhen_list += stock_data_next['data']
    # time.sleep(0.5)
    print(a_shenzhen_list)
    return a_shenzhen_list


def get_stock_sz(all_stock_list):
    shenzhen_stock_xlsx = f'http://www.szse.cn/api/report/ShowReport?'
    today = datetime.utcnow().strftime('%Y-%m-%d')
    yesterday = (datetime.utcnow() + timedelta(days=-1)).strftime('%Y-%m-%d')
    stock_xmls = {
        'SHOWTYPE': 'xlsx',
        'CATALOGID': '1815_stock_snapshot',
        'TABKEY': 'tab1',
        'txtBeginDate': today,
        'txtEndDate': today
    }
    shenzhen_stock_response = requests.get(url=shenzhen_stock_xlsx, params=stock_xmls)
    if shenzhen_stock_response.status_code == 200:
        filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.xlsx'
        with open(filename, 'wb') as f_stock:
            f_stock.write(shenzhen_stock_response.content)
        return parse_sz_xlsx(filename, all_stock_list)


def parse_sz_xlsx(filename, all_stock_list):
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), filename)

    df = pandas.read_excel(file_path, sheet_name='股票行情', dtype=str)
    for i in range(df.shape[0]):
        all_stock_list.append(TransactionDay(transaction_day=datetime.strptime(df.iat[i, 0], '%Y-%m-%d'),
                                             stock_code='sz' + df.iat[i, 1],
                                             stock_name=df.iat[i, 2],
                                             price_yesterday=float(df.iat[i, 3]),
                                             price_start=float(df.iat[i, 4]),
                                             price_high=float(df.iat[i, 5]),
                                             price_low=float(df.iat[i, 6]),
                                             price_end=float(df.iat[i, 7]),
                                             range_increase=float(df.iat[i, 8]),
                                             account_business=float(df.iat[i, 9].replace(',', '')),
                                             cash_business=float(df.iat[i, 10].replace(',', '')),
                                             pe_ration=float(df.iat[i, 11].replace(',', ''))
                                             ))


def get_stock_bs(stock_code: str, buy_list: list):
    bs_url = 'https://finance.sina.com.cn/finance/hq/upbs/{}.js?_=16'.format(stock_code)
    bs_response = requests.request(method='GET', url=bs_url, headers=headers, proxies=proxies)
    buy_flags = bs_response.text.split('/*')[0].strip().split('=')[1]
    if not buy_flags.__contains__('{') and not buy_flags.__contains__('}'):
        print(f'{stock_code} 没有B-S点信息')
    buy_dict = json.loads(buy_flags)
    if not buy_dict:
        print(f'{stock_code} 没有B-S点信息')
    for buy_date, buy_flag in buy_dict.items():
        buy_list.append(BuySale(stock_code=stock_code, spot_date=datetime.strptime(buy_date, '%Y-%m-%d'),
                                spot_type=buy_flag == '1'))


def handle_stock_bs(stock_list: list):
    stock_bs_list = []
    from concurrent.futures import ThreadPoolExecutor
    thread_pool = ThreadPoolExecutor(max_workers=30)
    for stock in stock_list:
        if str(stock.stock_code).startswith('sz300') \
                or str(stock.stock_code).startswith('sh688') \
                or str(stock.stock_code).startswith('sz301'):
            continue
        thread_pool.submit(get_stock_bs, stock.stock_code, stock_bs_list)
    thread_pool.shutdown(wait=True)
    return stock_bs_list


def get_all_stock(all_stock_list):
    sh_stock_list = get_stock_shanghai()
    get_stock_sz(all_stock_list)
    for sh_detail in sh_stock_list:
        all_stock_dict['sh' + sh_detail[0]] = sh_detail[7]
        all_stock_list.append(TransactionDay(transaction_day=datetime.strptime(today, '%Y-%m-%d'),
                                             stock_code='sh' + sh_detail[0],
                                             stock_name=sh_detail[1],
                                             price_yesterday=float(sh_detail[6]),
                                             price_start=float(sh_detail[2]),
                                             price_high=float(sh_detail[3]),
                                             price_low=float(sh_detail[4]),
                                             price_end=float(sh_detail[5]),
                                             range_increase=float(sh_detail[7]),
                                             account_business=int(sh_detail[8]),
                                             cash_business=float(sh_detail[9]),
                                             pe_ration=float(0)
                                             ))


if __name__ == '__main__':
    # shenzhen_stock_list = get_stock_shenzhen()
    # master_stock_all = []
    # for shenzhen_detail in shenzhen_stock_list:
    #     master_stock_all.append('sz' + shenzhen_detail['agdm'])
    # print(master_stock_all.__len__())
    # print(master_stock_all)
    # with open('test', 'w', encoding='utf-8') as stock_file:
    #     stock_file.writelines([line + '\n' for line in master_stock_all])

    # test_stock = ['sh600000', 'sh600004', 'sz002146', 'sz002452']
    # print(master_all.__len__())
    # print(json.dumps(handle_stock_bs(master_all)))

    # handle_stock_bs(get_all_stock())
    realTime_info = get_stock_realTime_sz('000151')
    print(realTime_info.change_rate)

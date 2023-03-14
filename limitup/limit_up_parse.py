import time

from sqlalchemy import and_

from exts import db
from get_stock_data import get_stock_realTime_sh, get_stock_realTime_sz
from models import LimitUp, TransactionDay, PreLimitUp
from utils.date_util import get_last_days, get_current_day
from . import limit


@limit.route('/parse_up')
def parse_limitUp():
    days = 2
    last_two_days = get_last_days(get_current_day(), -days)
    # 查询昨日涨停板，没有连板，存在回调情况的股票
    limit_up_lists = LimitUp.query.filter(LimitUp.transaction_day == last_two_days[0]).all()
    for limit_up_stock in limit_up_lists:
        if limit_up_stock.stock_code.startswith('sh'):
            stock_code = limit_up_stock.stock_code.strip('sh')
            stock_sh = get_stock_realTime_sh(stock_code)
            stock_name = 'SH-' + stock_sh.name
        if limit_up_stock.stock_code.startswith('sz'):
            stock_code = limit_up_stock.stock_code.strip('sz')
            stock_sh = get_stock_realTime_sz(stock_code)
            stock_name = 'SZ-' + stock_sh.name
            time.sleep(1)
        if stock_sh.price_start is not None:
            start_change_rate = round((float(
                stock_sh.price_start) - limit_up_stock.price_end) * 100 / limit_up_stock.price_end, 2)
        else:
            print('股票可能停牌', stock_sh.price_start)
            continue
        if float(stock_sh.price_high) > limit_up_stock.price_end:
            price_high = float(stock_sh.price_high)
        else:
            price_high = limit_up_stock.price_end
        high_change_rate = (price_high - float(stock_sh.price_current)) * 100 / limit_up_stock.price_end
        # if start_change_rate > 5 and limit_up_stock.limit_count == 1:
        #     print('{} - 高开股票 - 开盘涨幅:{} - 当前涨幅:{}'.format(stock_sh.name, start_change_rate, stock_sh.change_rate))
        if limit_up_stock.limit_count == 1:
            if limit_up_stock.price_end < 15 and start_change_rate >= 2 and abs(high_change_rate) >= 0:
                print('{} - 昨日涨停 -开盘涨幅 {} - 当前涨幅:{} - 当前振幅:{}'.
                      format(stock_name, start_change_rate, stock_sh.change_rate, high_change_rate))
            if start_change_rate < 0 and \
                    (limit_up_stock.price_end - float(stock_sh.price_low)) / limit_up_stock.price_end > 0.06:
                print('{} - 昨日涨停 - 开盘涨幅:{} - 当前降幅:{}'.format(stock_name, start_change_rate, stock_sh.change_rate))
            else:
                continue
        # elif start_change_rate > 3 and \
        #         abs(high_change_rate) > 0.05 and \
        #         limit_up_stock.continue_rise >= 2:
        #     print('{} - 连板- 开盘涨幅:{} - 当前振幅:{}'.format(stock_name, start_change_rate, high_change_rate))
        else:
            if start_change_rate > 3 and abs(high_change_rate) > 0.05 and limit_up_stock.continue_rise == 1:
                print('{} - 多次涨停- 开盘涨幅:{} - 当前振幅:{}'.format(stock_name, start_change_rate, high_change_rate))
    days = 6
    last_six_days = get_last_days(current_day=get_current_day(), window_size=-days)
    pre_limit_up_lists = PreLimitUp.query.filter(PreLimitUp.transaction_day >= last_six_days[0],
                                                 PreLimitUp.transaction_day <= last_six_days[-2]).all()
    for pre_limit_up_stock in pre_limit_up_lists:
        if pre_limit_up_stock.stock_code.startswith('sh'):
            stock_code = pre_limit_up_stock.stock_code.strip('sh')
            pre_stock_sh = get_stock_realTime_sh(stock_code)
            stock_name = 'SH-' + stock_sh.name
        if pre_limit_up_stock.stock_code.startswith('sz'):
            stock_code = pre_limit_up_stock.stock_code.strip('sz')
            pre_stock_sh = get_stock_realTime_sz(stock_code)
            stock_name = 'SZ-' + stock_sh.name
        if pre_stock_sh.price_high is None:
            continue
        if float(pre_stock_sh.price_high) > pre_limit_up_stock.price_end:
            price_high = float(pre_stock_sh.price_high)
        else:
            price_high = pre_limit_up_stock.price_end
        high_change_rate = (price_high - float(pre_stock_sh.price_low)) / pre_limit_up_stock.price_end
        if abs(high_change_rate) > 10:
            print('预涨停-冲高回落 - {} - {}'.format(stock_name, high_change_rate))

    return 'Hello world'


@limit.route('/parse_limitUp_long')
def parse_limitUp_long():
    days = 7
    last_six_days = get_last_days(current_day=get_current_day(), window_size=-days)
    # 查询最近6天的交易信息
    limit_up_lists = LimitUp.query.filter(and_(LimitUp.transaction_day < last_six_days[-2],
                                               LimitUp.transaction_day >= last_six_days[0],
                                               LimitUp.continue_rise >= 1)).all()
    for limit_up_stock in limit_up_lists:
        if limit_up_stock.stock_code.startswith('sh'):
            stock_code = limit_up_stock.stock_code.strip('sh')
            stock_sh = get_stock_realTime_sh(stock_code)

        if limit_up_stock.stock_code.startswith('sz'):
            stock_code = limit_up_stock.stock_code.strip('sz')
            stock_sh = get_stock_realTime_sz(stock_code)
        if limit_up_stock.price_high > float(stock_sh.price_high):
            price_high = limit_up_stock.price_high
        else:
            price_high = float(stock_sh.price_high)
        change_rate = (price_high - float(stock_sh.price_low)) / limit_up_stock.price_high
        if abs(change_rate) > (0.6 + (limit_up_stock.limit_count - 1) * 0.05) and float(stock_sh.price_low) < 20:
            print('{} 次数:{} 跌幅：{}，价格：{}'.format(stock_sh.name, limit_up_stock.limit_count, abs(change_rate),
                                                      float(stock_sh.price_current)))
    return 'Hello world'


@limit.route('/get_pre_limitUp')
def get_pre_limitUp():
    days = 2
    last_two_days = get_last_days('2023-03-14', -days)
    pre_stock_dict = {}
    stock_list = TransactionDay.query.filter(
        and_(TransactionDay.range_increase < 11,
             TransactionDay.transaction_day == last_two_days[1])).all()
    stock_list_yesterday = TransactionDay.query.filter(
        and_(TransactionDay.range_increase >= 9.9,
             TransactionDay.transaction_day == last_two_days[0])).all()
    stock_intersection_list = []
    for stock in stock_list:
        for stock_yesterday in stock_list_yesterday:
            if stock.stock_code == stock_yesterday.stock_code:
                stock_intersection_list.append(stock)
                continue
        if (stock.price_high - stock.price_yesterday) / stock.price_yesterday > 0.09 and \
                not stock.stock_code.startswith('sh300') and stock.price_end > stock.price_start:
            limit_up_lists = LimitUp.query.filter(LimitUp.stock_code == stock.stock_code).first()
            pre_limit_up = PreLimitUp.query.filter(PreLimitUp.stock_code == stock.stock_code).first()
            if limit_up_lists is None and pre_limit_up is not None:
                # 更新记录历史记录，或者插入新纪录
                pre_limit_up.transaction_day = stock.transaction_day
                pre_limit_up.price_end = stock.price_end
                pre_limit_up.price_high = stock.price_high
                db.session.add(pre_limit_up)
                db.session.commit()
            elif limit_up_lists is None and pre_limit_up is None:
                pre_limit_up_tmp = PreLimitUp(stock_code=stock.stock_code, stock_name=stock.stock_name,
                                              price_end=stock.price_end, transaction_day=stock.transaction_day,
                                              price_high=stock.price_high)
                db.session.add(pre_limit_up_tmp)
                db.session.commit()
            else:
                continue
            if stock.price_end < 20:
                print(stock.stock_code, stock.stock_name)
                pre_stock_dict[stock.stock_code] = stock.range_increase
    pre_limit_up_lists = PreLimitUp.query.filter(PreLimitUp.transaction_day < last_two_days[1]).all()
    for pre_limit_up in pre_limit_up_lists:
        stock_his_info = TransactionDay.query.filter(TransactionDay.transaction_day == last_two_days[1],
                                                     TransactionDay.stock_code == pre_limit_up.stock_code).first()
        if stock_his_info.price_high > pre_limit_up.price_high:
            pre_limit_up.price_high = stock_his_info.price_high
            pre_limit_up.transaction_day = stock_his_info.transaction_day
        db.session.add(pre_limit_up)
        db.session.commit()

    # for stock_upDown in stock_intersection_list:
    #     if (
    #             stock_upDown.price_high - stock_upDown.price_yesterday) / stock_upDown.price_yesterday > 0.09 and \
    #             stock_upDown.range_increase < 2:
    #         if stock_upDown.price_end < 15:
    #             print(stock_upDown.stock_code, stock_upDown.stock_name, '涨停回调')
    return 'Done'


@limit.route('/get_limitUp')
def get_limitUp():
    stock_list = []
    days = 2
    last_two_days = get_last_days('2023-03-14', -days)
    stock_list_1 = TransactionDay.query.filter(
        and_(TransactionDay.range_increase > 9.9, TransactionDay.range_increase < 11,
             TransactionDay.transaction_day == last_two_days[1])).all()
    for stock_today in stock_list_1:
        limit_up_lists = LimitUp.query.filter(LimitUp.stock_code == stock_today.stock_code).all()
        if limit_up_lists.__len__() >= 2:
            print('数据异常，请手动修复')
        if limit_up_lists.__len__() == 1:
            for limit_info in limit_up_lists:
                print(type(limit_info.transaction_day))
                # 如果昨天存在涨停，则更新日期及连涨字段等
                if limit_info.transaction_day.strftime('%Y-%m-%d') == last_two_days[0]:
                    limit_info.transaction_day = stock_today.transaction_day
                    limit_info.limit_count += 1
                    limit_info.continue_rise += 1
                    limit_info.price_end = stock_today.price_end
                    if stock_today.price_high > limit_info.price_high:
                        limit_info.price_high = stock_today.price_high
                    limit_info.nextDay_increase = 0
                    db.session.add(limit_info)
                    db.session.commit()
                elif limit_info.transaction_day.strftime('%Y-%m-%d') == last_two_days[1]:
                    continue
                else:
                    # 新纪录插入数据库
                    limit_info.transaction_day = stock_today.transaction_day
                    limit_info.limit_count += 1
                    limit_info.price_end = stock_today.price_end
                    limit_info.price_high = stock_today.price_high
                    limit_info.nextDay_increase = 0
                    db.session.add(limit_info)
                    db.session.commit()
        if limit_up_lists.__len__() == 0:
            print(stock_today.stock_name)
            limit_up = LimitUp(stock_code=stock_today.stock_code,
                               stock_name=stock_today.stock_name,
                               price_end=stock_today.price_end,
                               price_high=stock_today.price_high,
                               transaction_day=stock_today.transaction_day)
            stock_list.append(limit_up)
    if stock_list is not None:
        db.session.add_all(stock_list)
        db.session.commit()
    limit_up_lists = LimitUp.query.filter(LimitUp.transaction_day < last_two_days[1]).all()
    for limit_up in limit_up_lists:
        last_ten_days = get_last_days(get_current_day(), -10)
        if limit_up.transaction_day.strftime('%Y-%m-%d') < last_ten_days[0]:
            print(limit_up.stock_name)
            db.session.delete(limit_up)
            db.session.commit()
            continue
        else:
            current_stock_info = TransactionDay.query.filter(
                TransactionDay.stock_code == limit_up.stock_code,
                TransactionDay.transaction_day == last_two_days[1]).first()
        # 判断是否为昨天涨停，今天仍然高开的股票，这种股票要多关注
        if limit_up.transaction_day.strftime('%Y-%m-%d') == last_two_days[0] and \
                (
                        current_stock_info.price_start - current_stock_info.price_yesterday) / current_stock_info.price_yesterday > 2:
            limit_up.nextDay_increase = 1
        else:
            limit_up.nextDay_increase = 0
        if current_stock_info.price_high > limit_up.price_high:
            limit_up.price_high = current_stock_info.price_high
            db.session.add(limit_up)
            db.session.commit()

    return 'Done'

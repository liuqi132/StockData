from datetime import datetime, timedelta
import exchange_calendars as trade_date


def get_current_day():
    today = datetime.utcnow().strftime('%Y-%m-%d')
    return today


def get_yesterday():
    return (datetime.utcnow() + timedelta(days=-1)).strftime('%Y-%m-%d')


def get_last_days(current_day, window_size):
    trade_calendar = trade_date.get_calendar('XSHG')
    date_list = trade_calendar.sessions_window(current_day, window_size)
    return [x.strftime('%F') for x in date_list]


if __name__ == '__main__':
    print(get_last_days('2023-01-31', -3))
    print(type(datetime.today().date()))

import json

from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
from exts import db


class StockBaseInfo(db.Model):
    __tablename__ = 't_stock_baseInfo'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(16))
    stock_name = db.Column(db.String(32))


class TransactionDay(db.Model, dict):
    __tablename__ = 't_transaction_day'
    id = db.Column(db.Integer, primary_key=True)
    transaction_day = db.Column(db.Date, default=datetime.utcnow)
    stock_code = db.Column(db.String(16))
    stock_name = db.Column(db.String(32))
    price_yesterday = db.Column(db.Integer)
    price_start = db.Column(db.Float)
    price_high = db.Column(db.Float)
    price_low = db.Column(db.Float)
    price_end = db.Column(db.Float)
    range_increase = db.Column(db.Float)
    account_business = db.Column(db.Float)
    cash_business = db.Column(db.Float)
    pe_ration = db.Column(db.Float)

    def __init__(self):
        dict.__init__(self, transaction_day=self.transaction_day, stock_code=self.stock_code)

    __table_args__ = (
        db.UniqueConstraint('transaction_day', 'stock_code', name='unique_day_code'),
    )

    def to_json(self):
        return self.__dict__

    def __repr__(self):
        return f'{self.transaction_day}, {self.stock_code}, {self.stock_name}, {self.price_yesterday}, ' \
               f'{self.price_start} {self.price_high}, {self.price_low}, {self.price_end}, {self.range_increase}'


class BuySale(db.Model):
    __tablename__ = 't_stock_buy'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(16))
    spot_date = db.Column(db.Date)
    spot_type = db.Column(db.Boolean)

    __table_args__ = (
        db.UniqueConstraint('stock_code', 'spot_date', name='unique_code_date'),
    )

    def __repr__(self):
        return f'{self.stock_code}, {self.spot_date}, {self.spot_type}'


class LimitUp(db.Model):
    __tablename__ = 't_limit_up'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(16))
    stock_name = db.Column(db.String(32))
    price_end = db.Column(db.Float)
    price_high = db.Column(db.Float)
    transaction_day = db.Column(db.Date, default=datetime.utcnow)
    limit_count = db.Column(db.Integer, default=1)
    continue_rise = db.Column(db.Integer, default=1)
    create_time = db.Column(db.DateTime(), default=datetime.utcnow)
    nextDay_increase = db.Column(db.Boolean)

    __table_args__ = (
        db.UniqueConstraint('stock_code', 'transaction_day', name='unique_code_date'),
    )

    def __repr__(self):
        return f'{self.stock_code}, {self.stock_name}, {self.price_end}, {self.transaction_day}'


class PreLimitUp(db.Model):
    __tablename__ = 't_pre_limit_up'
    id = db.Column(db.Integer, primary_key=True)
    stock_code = db.Column(db.String(16))
    stock_name = db.Column(db.String(32))
    price_end = db.Column(db.Float)
    price_high = db.Column(db.Float)
    transaction_day = db.Column(db.Date, default=datetime.utcnow)
    create_time = db.Column(db.DateTime(), default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('stock_code', 'transaction_day', name='unique_code_date'),
    )

    def __repr__(self):
        return f'{self.stock_code}, {self.stock_name}, {self.price_end}, {self.transaction_day}'


if __name__ == '__main__':
    buy = BuySale(stock_code='11', spot_date='2023-01-12', spot_type='1')
    print(str(buy))

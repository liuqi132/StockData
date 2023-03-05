from flask_restful import Api, fields, marshal_with
from flask_restful.fields import MarshallingException
from datetime import datetime


class CustomDate(fields.Raw):
    def __init__(self, **kwargs):
        super(CustomDate, self).__init__(**kwargs)

    def format(self, value):
        try:
            return value.strftime('%Y-%m-%d')
        except AttributeError as ae:
            raise MarshallingException(ae)


transaction_fields = {
    'transaction_day': CustomDate,
    'stock_code': fields.String,
    'stock_name': fields.String,
    'price_yesterday': fields.Float,
    'price_start': fields.Float,
    'price_high': fields.Float,
    'price_low': fields.Float,
    'price_end': fields.Float,
    'range_increase': fields.Float,
    'account_business': fields.Float,
    'cash_business': fields.Float,
    'pe_ration': fields.Float
}

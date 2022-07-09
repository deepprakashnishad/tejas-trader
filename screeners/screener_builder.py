import json

from screeners.screener import Screener
from model import Screener as ScreenerDocument
from technicals.technical_condition import TechnicalCondition
from technicals.technical import *
from technicals.operators.m_operators import *


class ScreenerBuilder(Screener):

    def __init__(self, feed, screener_name, symbol_ids=None, start_time=None, end_time=None):
        screener_doc = ScreenerDocument.query.filter(ScreenerDocument.name == screener_name).first()
        super(ScreenerBuilder, self).__init__(position=screener_doc.transaction_type, name=screener_name,
                                              symbol_ids=symbol_ids, start_time=start_time, end_time=end_time,
                                              timeframe=screener_doc.timeframe,
                                              compression=screener_doc.compression, feed=feed)
        if len(self.symbol_ids) == 0:
            self.symbol_ids = symbol_ids

        for condition in screener_doc.entry_conditions:
            self.add_entry_conditions(
                self.get_condition(condition)
            )

    def get_condition(self, condition):
        return TechnicalCondition(
            technical1=self.get_technical_object(
                condition['technical1']['name'], condition['technical1']['tech_args']),
            operator=self.get_operator_object(condition['operator']['name'], condition['operator']['tech_args']),
            technical2=None if 'technical2' not in condition.keys() else
            self.get_technical_object(
                condition['technical2']['name'], condition['technical2']['tech_args'])
            ,
            timeframe_dict={},
            compression_dict={},
            symbol_ids_dict={}
        )

    def get_technical_object(self, condition_name, kwargs):
        if condition_name=="":
            return None
        return globals()[condition_name](self.feed, **kwargs)

    def get_operator_object(self, operator_name, kwargs):
        return globals()[operator_name](**kwargs)

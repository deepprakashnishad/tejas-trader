import json

from strategies.strategy import Strategy
from models.strategy import Strategy as StrategyDocument
from technicals.technical_condition import TechnicalCondition
from technicals.technical import *
from technicals.operators.m_operators import *
from utils.utilities import dotdict


class StrategyBuilder(Strategy):

    def __init__(self, feed, strategy_name, symbols=None, start_time=None, end_time=None):
        strategy_doc = StrategyDocument.get(**{"name":strategy_name})
        strategy_doc = dotdict(strategy_doc)
        if symbols is None:
            symbols = strategy_doc.symbols
        super(StrategyBuilder, self).__init__(position=strategy_doc.transaction_type, name=strategy_name,
                                              start_time=start_time, end_time=end_time,
                                              symbol_ids=symbols, timeframe=strategy_doc.timeframe,
                                              compression=strategy_doc.compression, feed=feed)

        for condition in strategy_doc.entry_conditions:
            self.add_entry_conditions(
                self.get_condition(condition)
            )

        for condition in strategy_doc.exit_conditions:
            self.add_exit_conditions(
                self.get_condition(condition)
            )

    def get_condition(self, condition):
        return TechnicalCondition(
            technical1=self.get_technical_object(
                condition['technical1']['name'], condition['technical1']['tech_args']),
            operator=self.get_operator_object(condition['operator']['name'], condition['operator']['tech_args']),
            technical2=None if 'technical2' not in condition.keys() or condition['technical2']['name']==""  else
            self.get_technical_object(
                condition['technical2']['name'], condition['technical2']['tech_args'])
            ,
            timeframe_dict=None,
            compression_dict=None,
            symbol_ids_dict=None
        )

    def get_technical_object(self, condition_name, kwargs):
        return globals()[condition_name](self.feed, **kwargs)

    def get_operator_object(self, operator_name, kwargs):
        return globals()[operator_name](**kwargs)

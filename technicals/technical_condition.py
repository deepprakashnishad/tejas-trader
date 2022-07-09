from core.dataseries import TimeFrame
from feeds.feed import Feed
import time


def set_technical_symbol_timeframe(mtechnical, timeframe, compression, symbol_id):
    mtechnical.set_timeframe(timeframe=timeframe, compression=compression)
    mtechnical.set_symbol_id(symbol_id)


class TechnicalCondition:
    feed: Feed
    min_periods_required = 1
    symbol_id = None
    timeframe_dict = None
    compression_dict = None

    def __init__(self, technical1, operator, technical2=None,
                 timeframe_dict=None, compression_dict=None, symbol_ids_dict=None):
        self.technical1 = technical1
        self.technical2 = technical2
        self.operator = operator
        self.symbol_ids_dict = symbol_ids_dict
        self.timeframe_dict = timeframe_dict
        self.compression_dict = compression_dict

    def set_symbol_timeframe(self, strategy_symbol_id, strategy_timeframe, strategy_compression):
        if not self.symbol_ids_dict or strategy_symbol_id not in self.symbol_ids_dict.keys() \
                or self.symbol_ids_dict[strategy_symbol_id] is None:
            self.symbol_ids_dict[strategy_symbol_id] = strategy_symbol_id

        if not self.timeframe_dict or strategy_symbol_id not in self.timeframe_dict.keys() \
                or self.timeframe_dict[strategy_symbol_id] is None:
            self.timeframe_dict[strategy_symbol_id] = strategy_timeframe

        if not self.compression_dict or strategy_symbol_id not in self.compression_dict.keys() \
                or self.compression_dict[strategy_symbol_id] is None:
            self.compression_dict[strategy_symbol_id] = strategy_compression

        set_technical_symbol_timeframe(self.technical1, self.timeframe_dict[strategy_symbol_id],
                                       self.compression_dict[strategy_symbol_id],
                                       self.symbol_ids_dict[strategy_symbol_id])
        if self.technical2 is not None:
            set_technical_symbol_timeframe(self.technical2, self.timeframe_dict[strategy_symbol_id],
                                           self.compression_dict[strategy_symbol_id],
                                           self.symbol_ids_dict[strategy_symbol_id])

    def is_satisfied(self, index):
        return self.operator.operate(index, self.technical1, self.technical2)

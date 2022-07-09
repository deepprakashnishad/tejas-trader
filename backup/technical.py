import time

from talib._ta_lib import *
import datetime
import pandas as pd
from core.dataseries import TimeFrame


def get_index(index, series):
    if index > -1:
        return index
    else:
        return len(series) - 1


class Technical:
    feed = {}
    minimal_periods = 1
    timeframe = TimeFrame.Minutes
    compression = 1
    symbol_id = None
    index = -1
    name = ""

    def __init__(self, feed, **kwargs):
        self.feed = feed

    def calculate_series(self, index, **kwargs):
        pass

    def calculate(self, index):
        pass

    def set_symbol_id(self, symbol_id):
        self.symbol_id = symbol_id

    def set_timeframe(self, timeframe, compression):
        self.timeframe = timeframe
        self.compression = compression

    def get_current_time(self, index):
        if index > -1:
            return self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)][index]['date']
        elif index < 0 and \
                (self.symbol_id, self.timeframe, self.compression) not in self.feed.data_dict.keys() \
                or len(self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]) == 0:
            return datetime.datetime.now()
        else:
            return self.feed.data_dict[(self.symbol_id, self.timeframe,
                                        self.compression)][len(self.feed.data_dict[(self.symbol_id, self.timeframe,
                                                                                    self.compression)]) - 1]['date']

    def prepare_feed(self, symbol_id, start_time, end_time,
                     timeframe=None, compression=None, batch_size=200, is_direction_forward=True):
        if timeframe is None:
            timeframe = self.timeframe
        if compression is None:
            compression = self.compression
        if symbol_id not in self.feed.instruments:
            self.feed.instruments.append(symbol_id)
        if end_time is None:
            end_time = self.feed.get_end_time(start_time, batch_size, timeframe, compression)

        self.feed.is_direction_forward = is_direction_forward
        self.feed.set_timeframe(timeframe=timeframe, compression=compression)
        self.feed.set_start_end_time(start_time=start_time, end_time=end_time)
        self.feed.set_fetch_batch_periods(fetch_batch_periods=batch_size)

    def get_data(self, minimal_period, start_time=datetime.datetime.now()):
        if (self.symbol_id, self.timeframe, self.compression) not in self.feed.data_dict.keys() or \
                len(self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]) < minimal_period:
            self.prepare_feed(self.symbol_id, start_time, self.feed.get_end_time(
                start=start_time, count=minimal_period, timeframe=self.timeframe,
                compression=self.compression, is_direction_forward=False))
            start = time.process_time()
            self.feed.fetch_and_load()
            print(f"Time for fetching data - {time.process_time() - start}")
        result = self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]
        return pd.DataFrame(result)

    def get_series(self, data_rows, key):
        series = []
        i = 0
        for data_row in data_rows:
            i = i + 1
            print(i)
            series.append(data_row[key])
        return series


class MySMA(Technical):
    def __init__(self, feed, **kwargs):
        self.period = kwargs['period']
        self.name = "SMA"
        super(MySMA, self).__init__(feed, minimal_period=10)

    def calculate_series(self, index, **kwargs):
        data = self.get_data(self.period, self.get_current_time(index))
        # data = self.get_series(data, 'close')
        data = data['close']
        return SMA(data, self.period)

    def calculate(self, index, **kwargs):
        data = self.get_data(self.period, self.get_current_time(index))['close']
        # data = self.get_series(data, 'close')
        data = data['close']
        result = SMA(data, self.period)
        index = get_index(index, result)
        return result[index]


class ClosePrice(Technical):
    def __init__(self, feed, minimal_period=1):
        self.name = "Close Price"
        super(ClosePrice, self).__init__(feed, minimal_period=minimal_period)

    def calculate_series(self, index, **kwargs):
        return self.feed.df_dict[(self.symbol_id, self.timeframe, self.compression)]['close']
        # return self.get_series(self.feed.df_dict[(self.symbol_id, self.timeframe, self.compression)], 'close')

    def calculate(self, index):
        result = self.feed.df_dict[(self.symbol_id, self.timeframe, self.compression)]['close']
        # result = self.get_series(self.feed.df_dict[(self.symbol_id, self.timeframe, self.compression)], 'close')
        index = get_index(index, result)
        return result[index]

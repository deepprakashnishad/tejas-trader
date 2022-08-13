import time

import talib._ta_lib as tal
from dateutil.tz import tzoffset
from pytz import tzinfo
from talib._ta_lib import *
import datetime
from core.dataseries import TimeFrame


def get_index(index, series):
    if index > -1:
        return index
    else:
        return len(series) - 1


class Technical:
    feed = {}
    minimal_periods = 200
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
            return self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]['date'][index]
        elif index < 0 and \
                (self.symbol_id, self.timeframe, self.compression) not in self.feed.data_dict.keys() \
                or len(self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]) == 0:
            return datetime.datetime.now()
        else:
            return self.feed.data_dict[(self.symbol_id, self.timeframe,
                                        self.compression)]['date'][
                len(self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]) - 1]

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

    def get_data(self, minimal_period, start_time=datetime.datetime.now(),
                 is_direction_forward=False, is_initial_setup=False):
        if (self.symbol_id, self.timeframe, self.compression) not in self.feed.data_dict.keys():
            # len(self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]) < minimal_period
            self.prepare_feed(self.symbol_id, start_time, self.feed.get_end_time(
                start=start_time, count=minimal_period, timeframe=self.timeframe,
                compression=self.compression, is_direction_forward=is_direction_forward))
            start = time.process_time()
            self.feed.fetch_and_load(start_time=start_time, timeframe=self.timeframe,
                                     compression=self.compression, is_direction_forward=is_direction_forward)
            print(f"Time for fetching data - {time.process_time() - start}")
        else:
            last_ts = self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)].loc(1)['date'][
                self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)].tail(1).index[-1]]
            if (last_ts + datetime.timedelta(
                    minutes=TimeFrame.get_interval_in_minutes(self.timeframe, self.compression))) > start_time:

                if "date" in self.feed.data_dict[self.symbol_id, self.timeframe, self.compression].keys():
                    last_dict_time = self.feed.data_dict[self.symbol_id,
                                                         self.timeframe, self.compression]['date'].iloc[-1]
                else:
                    last_dict_time = datetime.now(tz=tzoffset(None, 19800))

                    self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)] = \
                        self.feed.update_dict_with_new_data(self.feed.data_dict[(
                            self.symbol_id, self.timeframe, self.compression
                        )], self.feed.tick_dict[self.symbol_id].iloc[-1], last_dict_time, self.timeframe, self.compression)

        return self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]


class MovingAverage(Technical):
    def __init__(self, feed, **kwargs):
        self.period = kwargs['period']
        self.type = kwargs['type']
        if 'field' in kwargs:
            self.field = kwargs['field']
        else:
            self.field = 'close'
        self.name = "SMA"
        super(MovingAverage, self).__init__(feed, minimal_period=10)

    def calculate_series(self, index, **kwargs):
        data = self.get_data(self.period, self.get_current_time(index))
        data = data[self.field]
        if self.type == "simple":
            return SMA(data.values, self.period)
        elif self.type == "exponential":
            return EMA(data.values, self.period)
        elif self.type == "weighted":
            return WMA(data.values, self.period)
        elif self.type == "triple":
            return TEMA(data.values, self.period)
        elif self.type == "triangular":
            return TRIMA(data.values, self.period)
        elif self.type == "double":
            return DEMA(data.values, self.period)
        elif self.type == "kaufman":
            return KAMA(data.values, self.period)


class ClosePrice(Technical):
    def __init__(self, feed, **kwargs):
        self.name = "Close Price"
        super(ClosePrice, self).__init__(feed)

    def calculate_series(self, index, **kwargs):
        return self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]['close']


class PreviousHigh(Technical):
    def __init__(self, feed, **kwargs):
        self.name = "Previous High"
        super(PreviousHigh, self).__init__(feed)

    def calculate_series(self, index, **kwargs):
        data = self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]['high']
        return data.shift(periods=1)


class PreviousLow(Technical):
    def __init__(self, feed, **kwargs):
        self.name = "Previous Low"
        super(PreviousLow, self).__init__(feed)

    def calculate_series(self, index, **kwargs):
        data = self.feed.data_dict[(self.symbol_id, self.timeframe, self.compression)]['low']
        return data.shift(periods=1)


class RSI(Technical):
    def __init__(self, feed, **kwargs):
        self.period = kwargs['period']
        if 'field' in kwargs:
            self.field = kwargs['field']
        else:
            self.field = 'close'

        if 'minimal_period' in kwargs:
            self.minimal_periods = kwargs['minimal_period']
        else:
            self.minimal_periods = 14
        super(RSI, self).__init__(feed, minimal_period=self.minimal_periods+56)

    def calculate_series(self, index, **kwargs):
        data = self.get_data(self.period, self.get_current_time(index))
        data = data[self.field]
        return tal.RSI(data, timeperiod=int(self.period))


class DayFirstCandle(Technical):
    def __init__(self, feed, **kwargs):
        if 'field' in kwargs:
            self.field = kwargs['field']
        else:
            self.field = 'high'
        super(DayFirstCandle, self).__init__(feed)

    def calculate_series(self, index, **kwargs):
        current_time = self.get_current_time(index)
        data = self.get_data(self.field, current_time)
        time_series = data['timestamp']
        today_date = current_time.date()
        for i in range(0, len(time_series)):
            if today_date > time_series[i].date():
                break
        print(time_series[i-1])
        return data[self.field][i-1]


class Range(Technical):
    def __init__(self, feed, **kwargs):
        super(Range, self).__init__(feed)

    def calculate_series(self, index, **kwargs):
        data = self.get_data(self.period, self.get_current_time(index))
        return data['high']-data['low']


class TestCandle(Technical):
    def __init__(self, feed, **kwargs):
        self.candle_pattern = kwargs['candle_pattern']
        super(Technical, self).__init__(feed)

    def calculate_series(self, index, **kwargs):
        data = self.get_data(self.period, self.get_current_time(index))
        return globals()[self.candle_pattern](data['open'], data['high'], data['close'], data['close'])

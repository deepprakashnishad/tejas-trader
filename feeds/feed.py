import multiprocessing
import threading
from datetime import timedelta, datetime
from math import floor
from core.dataseries import TimeFrame
import pandas as pd


class Feed(TimeFrame):
    live_feed_queue = multiprocessing.Queue()
    e: threading.Event
    tick_dict = multiprocessing.Manager().dict()
    data_dict = {}
    last_ts = {}
    timeframe = 4
    compression = 1
    start_time = datetime.now()
    end_time = datetime.now()
    is_direction_forward = True
    fetch_batch_periods = 5000
    instruments = []
    tick_flag = False

    def fetch_and_load(self, symbol_id, timeframe, compression, is_direction_forward):
        pass

    # def load_data(self):
    #     pass

    def fetch_data(self):
        pass

    def monitor_live_data(self, symbols):
        pass

    def on_tick_recieved(self, ticks):
        pass

    def set_timeframe(self, timeframe, compression):
        self.timeframe = timeframe
        self.compression = compression

    def set_start_end_time(self, start_time, end_time=None):
        self.start_time = start_time
        self.end_time = end_time

    def set_from_start(self, is_from_start):
        self.is_direction_forward = is_from_start

    def set_fetch_batch_periods(self, fetch_batch_periods):
        self.fetch_batch_periods = fetch_batch_periods

    def __len__(self):
        return len(self.data)

    def get_data_points(self, count, start_index, order="asc"):
        if order == "asc":
            return self.data[start_index: start_index + count]
        else:
            return self.data[start_index: start_index - count]

    def set_column_headers(self, columns):
        self.data.columns = columns

    def remove_column_header(self, column):
        del self.data[column]

    def get_end_time(self, start, count, timeframe, compression, is_direction_forward=True):
        if is_direction_forward:
            if timeframe == 3:
                return start + timedelta(seconds=count * compression)
            elif timeframe == 4:
                return start + timedelta(minutes=count * compression)
            elif timeframe == 5:
                return start + timedelta(days=count * compression)
            elif timeframe == 6:
                return start + timedelta(weeks=count * compression)
            elif timeframe == 7:
                return start + timedelta(days=count * compression * 30)
            elif timeframe == 8:
                return start + timedelta(days=count * compression * 365)

        else:
            if timeframe == 3:
                return start - timedelta(seconds=count * compression)
            elif timeframe == 4:
                return start - timedelta(minutes=count * compression)
            elif timeframe == 5:
                return start - timedelta(days=count * compression)
            elif timeframe == 6:
                return start - timedelta(weeks=count * compression)
            elif timeframe == 7:
                return start - timedelta(days=count * compression * 30)
            elif timeframe == 8:
                return start - timedelta(days=count * compression * 365)

    def update_dict_with_new_data(self, ldict, tick, last_dict_time, timeframe, compression):
        total_minutes = TimeFrame.get_interval_in_minutes(timeframe, compression)

        if last_dict_time + timedelta(minutes=total_minutes) > tick['date']:
            last_index = ldict.tail(1).index[-1]
            # df = ldict.copy(deep=True)
            ldict.iat[last_index, 2] = max(tick['high'], ldict.loc(1)['high'][last_index])

            ldict.iat[last_index, 3] = min(tick['low'], ldict.loc(1)['low'][last_index])

            ldict.iat[last_index, 4] = tick['close']

            ldict.iat[last_index, 5] = tick['volume'] + ldict.loc(1)['volume'][last_index]

            ldict.iat[last_index, 6] = tick['oi']
        else:
            if self.timeframe == TimeFrame.Minutes:
                time = tick['date'].replace(minute=floor(
                    tick['date'].minute/total_minutes)*total_minutes, second=0, microsecond=0)
            elif self.timeframe == TimeFrame.Days:
                time = tick['date'].replace(hour=0, minute=0, second=0, microsecond=0)

            ldict = ldict.append({
                "date": time,
                "open": tick['open'],
                "high": tick['high'],
                "low": tick['low'],
                "close": tick['close'],
                "volume": tick['volume'],
                "oi": tick['oi']
            }, ignore_index=True)

        print("Main Dataframe")
        print(ldict)
        return ldict
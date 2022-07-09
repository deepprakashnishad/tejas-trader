import datetime
from math import floor

from dateutil.tz import tzoffset
from pytz import timezone

from brokers.alpha_broker import AlphaBroker
from brokers.zerodha_broker import ZerodhaBroker
from core.dataseries import TimeFrame
from core.tejas import Tejas
from feeds.feed import Feed
import pandas as pd

from model import HistoricalData


class MongoFeed(Feed):
    # Supported granularities
    _GRANULARITIES = {
        (TimeFrame.Minutes, 1): '1min',
        (TimeFrame.Minutes, 5): '5min',
        (TimeFrame.Minutes, 15): '15min',
        (TimeFrame.Minutes, 30): '30min',
        (TimeFrame.Minutes, 60): '60min',
        (TimeFrame.Days, 1): 'day',
    }

    tejas: Tejas
    mtimezone = timezone('Asia/Kolkata')
    last_updated_db_time = datetime.datetime.now(tz=tzoffset(None, 19800))

    # df_dict = {}

    def get_interval(self, timeframe, compression):
        return self._GRANULARITIES[(timeframe, compression)]

    def __init__(self, broker=None):
        self.broker = broker

    def fetch_and_load(self, start_time=None, timeframe=None, compression=None, is_direction_forward=True):
        if start_time is None:
            start_time = self.start_time

        if timeframe is None:
            timeframe = self.timeframe

        if compression is None:
            compression = self.compression

        self.fetch_data(start_time=start_time, timeframe=timeframe, compression=compression,
                        is_direction_forward=is_direction_forward)

    def fetch_data(self, start_time=None, timeframe=4, compression=1, is_direction_forward=True):
        if start_time is None:
            start_time = self.start_time

        while True:
            all_instruments_fetched = True

            for instrument in self.instruments:
                if (instrument, timeframe, compression) in self.last_ts and \
                        ((
                                 is_direction_forward and
                                 (
                                         self.last_ts[(instrument, timeframe, compression)] >= self.end_time or
                                         self.last_ts[(instrument, timeframe, compression)] >=
                                         datetime.datetime.now(tz=tzoffset(None, 19800))
                                 )
                         ) or (
                                 not is_direction_forward and
                                 len(self.data_dict[(instrument, timeframe, compression)]) >= self.fetch_batch_periods
                         )):
                    continue
                else:
                    all_instruments_fetched = False

                if is_direction_forward:
                    end_time = self.get_end_time(start_time, self.fetch_batch_periods,
                                                 timeframe, compression, is_direction_forward)
                    data = self.broker.get_historical_data(
                        instrument_token=instrument,
                        from_date=start_time,
                        to_date=end_time
                    )
                else:
                    end_time = self.get_end_time(start_time, self.fetch_batch_periods,
                                                 timeframe, compression, is_direction_forward)
                    data = self.broker.get_historical_data(
                        instrument_token=instrument,
                        from_date=end_time,
                        to_date=start_time
                    )
                data = sorted(data, key=lambda k: k['date'])
                self.last_ts[(instrument, timeframe, compression)] = end_time
                start_time = end_time
                temp = pd.DataFrame(data)
                if (instrument, timeframe, compression) in self.data_dict.keys():
                    if is_direction_forward:
                        self.data_dict[(instrument, timeframe, compression)] = \
                            self.data_dict[(instrument, timeframe, compression)].append(temp, ignore_index=True)
                    else:
                        self.data_dict[(instrument, timeframe, compression)] = \
                            temp.append(self.data_dict[(instrument, timeframe, compression)], ignore_index=True)
                else:
                    self.data_dict[(instrument, timeframe, compression)] = temp

            if all_instruments_fetched:
                print("Initial data loading completed from mongodb")
                break

    def monitor_live_data(self, symbol_ids):
        self.broker.feed = self
        self.broker.sample_tick_generator()

    def subscribe_instruments(self, instrument_tokens):
        self.broker.subscribe(instrument_tokens)

    def set_broker(self, broker):
        self.broker = broker

    def on_tick_recieved(self, ticks):
        timeframe = 4
        compression = 1
        total_minutes = TimeFrame.get_interval_in_minutes(timeframe, compression)
        for tick in ticks:
            symbol = tick['instrument_token']
            if "timestamp" in tick.keys():
                current_time = tick['timestamp']
                current_time = self.mtimezone.localize(current_time)
            else:
                current_time = datetime.now(tz=tzoffset(None, 19800))

            if symbol in self.tick_dict.keys() and \
                    self.tick_dict[symbol].loc(1)['date'][self.tick_dict[symbol].tail(1).index[-1]] \
                    + datetime.timedelta(minutes=total_minutes) > current_time:
                last_index = self.tick_dict[symbol].tail(1).index[-1]
                df = self.tick_dict[symbol].copy(deep=True)
                df.iat[last_index, 2] = max(tick['ohlc']['high'], self.tick_dict[symbol].loc(1)['high'][last_index])

                df.iat[last_index, 3] = min(tick['ohlc']['low'], self.tick_dict[symbol].loc(1)['low'][last_index])

                df.iat[last_index, 4] = tick['ohlc']['close']

                df.iat[last_index, 5] = tick['volume'] + self.tick_dict[symbol].loc(1)['volume'][last_index]

                df.iat[last_index, 6] = tick['oi']
                self.tick_dict[symbol] = df.copy(deep=True)
            else:
                time = self.mtimezone.localize(tick['timestamp']).replace(
                    minute=(floor(tick['timestamp'].minute)), second=0, microsecond=0)

                if symbol not in self.tick_dict.keys():
                    self.tick_dict[symbol] = pd.DataFrame(columns=[
                        "date", "open", "high", "low", "close", "volume", "oi"
                    ])

                self.tick_dict[symbol] = self.tick_dict[symbol].append({
                    "date": time,
                    "open": tick['ohlc']['open'],
                    "high": tick['ohlc']['high'],
                    "low": tick['ohlc']['low'],
                    "close": tick['ohlc']['close'],
                    "volume": tick['volume'],
                    "oi": tick['oi']
                }, ignore_index=True)
        self.tick_flag = True

    def load_data(self, ohlcv):
        self.data.append()

from math import floor

from dateutil.tz import tzoffset
from pytz import timezone

from core.tejas import Tejas
from feeds.feed import Feed
from core.dataseries import *
import pandas as pd
from brokers.zerodha_broker import ZerodhaBroker
from utils import my_constants as mconst
import datetime


class ZerodhaFeed(Feed):
    # Supported granularities
    _GRANULARITIES = {
        (TimeFrame.Minutes, 1): 'minute',
        (TimeFrame.Minutes, 3): '3minute',
        (TimeFrame.Minutes, 5): '5minute',
        (TimeFrame.Minutes, 15): '15minute',
        (TimeFrame.Minutes, 30): '30minute',
        (TimeFrame.Minutes, 60): '60minute',
        (TimeFrame.Days, 1): 'day',
    }

    tejas: Tejas
    mtimezone = timezone('Asia/Kolkata')
    last_updated_db_time = datetime.datetime.now(tz=tzoffset(None, 19800))

    # df_dict = {}

    def get_interval(self, timeframe, compression):
        return self._GRANULARITIES[(timeframe, compression)]

    def __init__(self, broker=None):
        if broker is None:
            self.zerodha = ZerodhaBroker(mconst.UID)
        else:
            self.zerodha = broker

    def fetch_and_load(self, start_time=None, timeframe=None, compression=None, is_direction_forward=True):
        if start_time is None:
            start_time = self.start_time

        if timeframe is None:
            timeframe = self.timeframe

        if compression is None:
            compression = self.compression

        self.fetch_data(start_time, timeframe, compression, is_direction_forward)

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
                    data = self.zerodha.get_historical_data(
                        instrument_token=instrument,
                        interval=self.get_interval(self.timeframe, self.compression),
                        continuous=False,
                        oi=1,
                        from_date=start_time,
                        to_date=end_time
                    )
                else:
                    end_time = self.get_end_time(start_time, self.fetch_batch_periods,
                                                 timeframe, compression, is_direction_forward)
                    data = self.zerodha.get_historical_data(
                        instrument_token=instrument,
                        interval=self.get_interval(self.timeframe, self.compression),
                        continuous=False,
                        oi=1,
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
                print("Initial data loading completed")
                print(self.data_dict)
                break

    def monitor_live_data(self, symbol_ids):
        self.zerodha.feed = self
        # self.zerodha.sample_tick_generator()
        self.zerodha.connect(threaded=True, symbol_ids=symbol_ids)

    def subscribe_instruments(self, instrument_tokens):
        self.zerodha.subscribe(instrument_tokens)

    def set_broker(self, broker):
        self.zerodha = broker

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
        # self.live_feed_queue.put([1])
        # for tick in ticks:
        #     symbol = tick['instrument_token']
        #     if "timestamp" in tick.keys():
        #         current_time = tick['timestamp']
        #         current_time = self.mtimezone.localize(current_time)
        #     else:
        #         current_time = datetime.now(tz=tzoffset(None, 19800))
        #
        #     if symbol in self.tick_dict.keys() and \
        #             list(self.tick_dict[symbol].keys())[-1] + datetime.timedelta(minutes=total_minutes) > current_time:
        #         date_keys = list(self.tick_dict[symbol].keys())
        #         self.tick_dict[symbol][date_keys[-1]]['high'] = max(tick['ohlc']['high'],
        #                                                  self.tick_dict[symbol][date_keys[-1]]['high'])
        #
        #         self.tick_dict[symbol][date_keys[-1]]['low'] = min(tick['ohlc']['low'],
        #                                                 self.tick_dict[symbol][date_keys[-1]]['low'])
        #
        #         self.tick_dict[symbol][date_keys[-1]]['close'] = tick['ohlc']['close']
        #
        #         self.tick_dict[symbol][date_keys[-1]]['volume'] = tick['volume'] + \
        #                                                           self.tick_dict[symbol][date_keys[-1]]['volume']
        #
        #         self.tick_dict[symbol][date_keys[-1]]['oi'] = tick['oi']
        #     else:
        #         time = self.mtimezone.localize(tick['timestamp']).replace(
        #             minute=(floor(tick['timestamp'].minute)), second=0, microsecond=0)
        #
        #         if symbol not in self.tick_dict.keys():
        #             self.tick_dict[symbol] = {}
        #         self.tick_dict[symbol][time] = {}
        #         print(self.tick_dict)
        #         self.tick_dict[symbol][time]["open"] = tick['ohlc']['open']
        #         self.tick_dict[symbol][time]["high"] = tick['ohlc']['high']
        #         self.tick_dict[symbol][time]["low"] = tick['ohlc']['low']
        #         self.tick_dict[symbol][time]["close"] = tick['ohlc']['close']
        #         self.tick_dict[symbol][time]["volume"] = tick['volume']
        #         self.tick_dict[symbol][time]["oi"] = tick['oi']

        # for tick in ticks:
        #     symbol = tick['instrument_token']
        #     if "timestamp" in tick.keys():
        #         current_time = tick['timestamp']
        #         current_time = self.mtimezone.localize(current_time)
        #     else:
        #         current_time = datetime.now(tz=tzoffset(None, 19800))
        #
        #     if (symbol, self.timeframe, self.compression) in self.data_dict.keys() and \
        #             self.data_dict[(symbol, self.timeframe, self.compression)].loc(1)['date'][
        #                 self.data_dict[(symbol, self.timeframe, self.compression)].tail(1).index[-1]
        #             ] + datetime.timedelta(minutes=total_minutes) > current_time:
        #
        #         self.data_dict[(symbol, self.timeframe, self.compression)].at[
        #             self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'high'
        #         ] = max(tick['ohlc']['high'],
        #                 self.data_dict[(symbol, self.timeframe, self.compression)].loc(1)['high'][
        #                     self.data_dict[(symbol, self.timeframe, self.compression)].tail(1).index[-1]])
        #
        #         self.data_dict[(symbol, self.timeframe, self.compression)].at[
        #             self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'low'
        #         ] = min(tick['ohlc']['low'],
        #                 self.data_dict[(symbol, self.timeframe, self.compression)].loc(1)['low'][
        #                     self.data_dict[(symbol, self.timeframe, self.compression)].tail(1).index[-1]])
        #
        #         self.data_dict[(symbol, self.timeframe, self.compression)].at[
        #             self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'close'
        #         ] = tick['ohlc']['close']
        #
        #         self.data_dict[(symbol, self.timeframe, self.compression)].at[
        #             self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'volume'
        #         ] = tick['volume'] + self.data_dict[(symbol, self.timeframe, self.compression)].loc(1)['volume'][
        #                     self.data_dict[(symbol, self.timeframe, self.compression)].tail(1).index[-1]]
        #
        #         self.data_dict[(symbol, self.timeframe, self.compression)].at[
        #             self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'oi'
        #         ] = tick['oi']
        #     else:
        #         if self.timeframe == TimeFrame.Minutes:
        #             time = self.mtimezone.localize(tick['timestamp']).replace(
        #                 minute=(floor(tick['timestamp'].minute / self.compression) * self.compression)
        #                 , second=0, microsecond=0)
        #         if self.timeframe == TimeFrame.Days:
        #             time = self.mtimezone.localize(tick['timestamp']).replace(
        #                 hour=9, minute=15, second=0, microsecond=0)
        #
        #         if (symbol, self.timeframe, self.compression) in self.data_dict.keys():
        #             self.data_dict[(symbol, self.timeframe, self.compression)].loc[len(
        #                 self.data_dict[(symbol, self.timeframe, self.compression)])] = [
        #                 time,
        #                 tick['ohlc']['open'],
        #                 tick['ohlc']['high'],
        #                 tick['ohlc']['low'],
        #                 tick['ohlc']['close'],
        #                 tick['volume'],
        #                 tick['oi']
        #             ]
        #         else:
        #             self.data_dict[(symbol, self.timeframe, self.compression)] = pd.DataFrame(columns=[
        #                 "date", "open", "high", "low", "close", "volume", "oi"
        #             ])
        #             self.data_dict[(symbol, self.timeframe, self.compression)].loc[0] = [
        #                 time,
        #                 tick['ohlc']['open'],
        #                 tick['ohlc']['high'],
        #                 tick['ohlc']['low'],
        #                 tick['ohlc']['close'],
        #                 tick['volume'],
        #                 tick['oi']
        #             ]

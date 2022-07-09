from math import floor

from dateutil.tz import tzoffset
from pytz import timezone
from feeds.feed import Feed
from core.dataseries import *
import pandas as pd
from brokers.zerodha_broker import ZerodhaBroker
from strategies.strategy import Strategy
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

    strategy_obj: Strategy
    mtimezone = timezone('Asia/Kolkata')

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
                        oi=True,
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
                        oi=True,
                        from_date=end_time,
                        to_date=start_time
                    )

                temp = sorted(data, key=lambda k: k['date'])
                # if is_direction_forward:
                # self.last_ts[(instrument, timeframe, compression)] = data[len(data) - 1]['date']
                self.last_ts[(instrument, timeframe, compression)] = end_time
                start_time = end_time
                # else:
                #     self.last_ts[(instrument, timeframe, compression)] = data[0]['date']
                #     start_time = end_time

                if (instrument, timeframe, compression) in self.data_dict.keys():
                    if is_direction_forward:
                        self.data_dict[(instrument, timeframe, compression)] = \
                            self.data_dict[(instrument, timeframe, compression)] + temp
                        # self.data_dict[(instrument, timeframe, compression)] = \
                        #     self.data_dict[(instrument, timeframe, compression)].append(temp, ignore_index=True)
                    else:
                        self.data_dict[(instrument, timeframe, compression)] = \
                            temp + self.data_dict[(instrument, timeframe, compression)]
                else:
                    self.data_dict[(instrument, timeframe, compression)] = temp

            if all_instruments_fetched:
                print("Initial data loading completed")
                break

    def monitor_live_data(self, symbol_ids, timeframe, compression, strategy_obj):
        self.zerodha.feed = self
        self.timeframe = timeframe
        self.compression = compression
        self.strategy_obj = strategy_obj
        print("Monitoring about to start")
        self.zerodha.connect(threaded=False, symbol_ids=symbol_ids)

    def subscribe_instruments(self, instrument_tokens):
        self.zerodha.subscribe(instrument_tokens)

    def on_tick_recieved(self, ticks):
        print(f"Tick recieved at {datetime.datetime.now()}")
        total_minutes = self.compression
        if self.timeframe == TimeFrame.Minutes:
            total_minutes = self.compression
        elif self.timeframe == TimeFrame.Days:
            total_minutes = self.compression * 24 * 60
        for tick in ticks:
            print(tick)
            symbol = tick['instrument_token']
            if "timestamp" in tick.keys():
                current_time = tick['timestamp']
                current_time = self.mtimezone.localize(current_time)
            else:
                current_time = datetime.now(tz=tzoffset(None, 19800))

            if self.data_dict[(symbol, self.timeframe, self.compression)].loc(1)['date'][
                self.data_dict[(symbol, self.timeframe, self.compression)].tail(1).index[-1]
            ] + datetime.timedelta(minutes=total_minutes) > current_time:
                self.data_dict[(symbol, self.timeframe, self.compression)].at[
                    self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'open'
                ] = tick['ohlc']['open']
                self.data_dict[(symbol, self.timeframe, self.compression)].at[
                    self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'high'
                ] = tick['ohlc']['high']
                self.data_dict[(symbol, self.timeframe, self.compression)].at[
                    self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'low'
                ] = tick['ohlc']['low']
                self.data_dict[(symbol, self.timeframe, self.compression)].at[
                    self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'close'
                ] = tick['ohlc']['close']
                self.data_dict[(symbol, self.timeframe, self.compression)].at[
                    self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'volume'
                ] = tick['volume']
                self.data_dict[(symbol, self.timeframe, self.compression)].at[
                    self.data_dict[(symbol, self.timeframe, self.compression)].index[-1], 'oi'
                ] = tick['oi']
            else:
                if self.timeframe == TimeFrame.Minutes:
                    time = self.mtimezone.localize(tick['timestamp']).replace(
                        minute=(floor(tick['timestamp'].minute / self.compression) * self.compression)
                        , second=0, microsecond=0)
                if self.timeframe == TimeFrame.Days:
                    time = self.mtimezone.localize(tick['timestamp']).replace(
                        hour=9, minute=15, second=0, microsecond=0)

                self.data_dict[(symbol, self.timeframe, self.compression)].loc[len(
                    self.data_dict[(symbol, self.timeframe, self.compression)])] = [
                    time,
                    tick['ohlc']['open'],
                    tick['ohlc']['high'],
                    tick['ohlc']['low'],
                    tick['ohlc']['close'],
                    tick['volume'],
                    tick['oi']
                ]
            self.strategy_obj.run_live_mode()
        # Update dataframe dicttionary and Call strategy with new tick

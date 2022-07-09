from dateutil.tz import tzoffset
from core.tejas_run_modes import TejasRunModes
from technicals.technical_condition import TechnicalCondition
from datetime import datetime
from termcolor import colored


class Screener:
    name = ""
    entry_conditions: [TechnicalCondition] = []
    # # Dictionary object containing stoploss type(abs, percent) and its' value
    stoploss = {type: "percent", "value": 1}

    # # Dictionary object with type(abs, percent, none) and it's value
    target = {type: "percent", "value": 5}

    runmode = TejasRunModes.BACKTEST

    def __init__(self, position,  symbol_ids, timeframe=4, compression=15, start_time=None,
                 end_time=None, fetch_batch_periods=5000, name="", feed=None, symbols=[]):
        self.position = position
        self.name = name
        self.timeframe = timeframe
        self.compression = compression
        self.fetch_batch_periods = fetch_batch_periods
        self.symbol_ids = symbol_ids
        if start_time is None:
            self.runmode = TejasRunModes.LIVE
            self.start_time = datetime.now(tz=tzoffset(None, 19800))
        else:
            self.start_time = start_time
            self.runmode = TejasRunModes.BACKTEST

        if end_time is not None:
            self.end_time = end_time
        else:
            self.end_time = datetime.now(tz=tzoffset(None, 19800))

        self.feed = feed

    def set_feed(self, feed):
        self.feed = feed

    def add_entry_conditions(self, technical_condition):
        self.entry_conditions.append(technical_condition)

    def remove_entry_conditions(self, technical_condition):
        self.entry_conditions.remove(technical_condition)

    def set_primary_timeframe(self, timeframe, compression):
        self.timeframe = timeframe
        self.compression = compression

    def prepare_feed(self, symbol_id, start_time, end_time=None,
                     timeframe=None, compression=None, batch_size=5000, is_direction_forward=True):
        if timeframe is None:
            timeframe = self.timeframe
        if compression is None:
            compression = self.compression

        if symbol_id not in self.feed.instruments:
            self.feed.instruments.append(symbol_id)
        self.feed.set_timeframe(timeframe=timeframe, compression=compression)
        self.feed.set_start_end_time(start_time=start_time, end_time=end_time)
        self.feed.set_fetch_batch_periods(fetch_batch_periods=batch_size)
        self.feed.fetch_and_load(is_direction_forward=is_direction_forward)

    def execute(self):
        self.feed.set_from_start(False)
        for symbol_id in self.symbol_ids:
            self.prepare_feed(symbol_id, self.start_time, self.end_time,
                              self.timeframe, self.compression,
                              is_direction_forward=False, batch_size=self.fetch_batch_periods)
        self.feed.monitor_live_data(self.symbol_ids, self.timeframe, self.compression, self)

    def test_conditions(self, symbol_id):
        for technical_condition in self.entry_conditions:
            if not technical_condition.is_satisfied(-1):
                return False
        print(colored(f"{symbol_id} - Screening passed", "green"))
        return True

    def set_technical_condition_symbol_timeframe(self, symbol_id):
        for technical_condition in self.entry_conditions:
            technical_condition.set_symbol_timeframe(symbol_id, self.timeframe, self.compression)

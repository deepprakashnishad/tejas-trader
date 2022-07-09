from model import HistoricalData


class DBLoader:

    def __init__(self, feed, symbol_ids, timeframe, compression, start_time=None, end_time=None, batch_size=5000):
        self.symbol_ids = symbol_ids
        self.feed = feed
        self.timeframe = timeframe
        self.compression = compression
        self.start_time = start_time
        self.batch_size = batch_size

        if end_time is not None:
            self.end_time = end_time

    def prepare_feed(self, symbol_id, start_time, end_time, timeframe=None, compression=None, batch_size=5000):
        if timeframe is None:
            timeframe = self.timeframe
        if compression is None:
            compression = self.compression

        if symbol_id not in self.feed.instruments:
            self.feed.instruments.append(symbol_id)
        self.feed.set_timeframe(timeframe=timeframe, compression=compression)
        self.feed.set_start_end_time(start_time=start_time, end_time=end_time)
        self.feed.set_fetch_batch_periods(fetch_batch_periods=batch_size)
        self.feed.fetch_and_load()

    def load_data(self):
        for symbol_id in self.symbol_ids:
            self.prepare_feed(symbol_id, self.start_time, self.end_time, self.timeframe, self.compression,
                              self.batch_size)
        self.load_data_to_db()

    def load_data_to_db(self):
        for key in self.feed.df_dict.keys():
            for row in self.feed.df_dict[key].iterrows():
                data = HistoricalData(
                    symbol_id=key[0],
                    open=row[1]['open'],
                    high=row[1]['high'],
                    low=row[1]['low'],
                    close=row[1]['close'],
                    volume=row[1]['volume'],
                    open_interest=row[1]['oi'],
                    timeframe=key[1],
                    compression=key[2],
                    candle_creation_time=row[1]['date'],
                )
                data.save()
        print("Data saved successfully to mongodb")

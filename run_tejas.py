from dateutil.tz import tzoffset

from brokers.test_broker import TestBroker
from brokers.zerodha_broker import ZerodhaBroker
from brokers.alpha_broker import AlphaBroker
from core.tejas_run_modes import TejasRunModes
from feeds.db_loader import DBLoader
from feeds.zerodhafeed import ZerodhaFeed
from feeds.mongofeed import MongoFeed
from core.tejas import Tejas
from strategies.strategy_builder import StrategyBuilder
from technicals.technical import *
from utils import my_constants as mconst
from datetime import datetime


def __main__():
    feed = ZerodhaFeed(broker=None)
    # feed = MongoFeed(broker=None)
    tejas = Tejas(feed=feed, mode=TejasRunModes.LIVE, plot=True)
    broker = ZerodhaBroker(uid=mconst.UID)
    # broker = AlphaBroker()
    tejas.set_broker(broker)
    feed.set_broker(broker)

    tejas.add_strategy(StrategyBuilder(feed, strategy_name="NR7 Buy",
                                       start_time=datetime(2020, 3, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
                                       end_time=datetime(2020, 3, 12, 12, 9, tzinfo=tzoffset(None, 19800))))

    tejas.run()
    
    tejas.add_strategy(StrategyBuilder(feed, strategy_name="NR7 Short",
                                       start_time=datetime(2020, 3, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
                                       end_time=datetime(2020, 3, 12, 12, 9, tzinfo=tzoffset(None, 19800))))


# def __load_db__():
#     symbol_ids = [3050241]
#
#     db_loader = DBLoader(feed, start_time=datetime(2018, 1, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
#                          end_time=datetime(2018, 3, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
#                          symbol_ids=symbol_ids, timeframe=4, compression=5)
#
#     db_loader.load_data()


__main__()

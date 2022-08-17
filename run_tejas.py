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
from models.deploy_strategy import DeployStrategy
import time

def start_tejas():
    
    feed = ZerodhaFeed(broker=None)
    tejas = Tejas(feed=feed, mode=TejasRunModes.LIVE, plot=True)
    # broker = ZerodhaBroker(uid=mconst.UID)
    # if broker is None:
    #     return "Unable to initiate broker"
    # tejas.set_broker(broker)
    # feed.set_broker(broker)
    
    deployed_strategies = DeployStrategy.getMany()
    final_list = []
    for user_strategies in deployed_strategies:
        final_list = list(set(final_list) | set(user_strategies['strategy_ids']))
    final_list = [i for i in final_list if i is not None]
    print(final_list)
    
    for id in final_list:
        tejas.add_strategy(StrategyBuilder(feed, strategy_id=id,
                                       start_time=datetime(2020, 3, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
                                       end_time=datetime(2020, 3, 12, 12, 9, tzinfo=tzoffset(None, 19800))))
    print(tejas._strategies)
    tejas.run()
    return "Tejas Started"

# def __main__():
#     print("Starting Tejas")
#     start_tejas()


# def __load_db__():
#     symbol_ids = [3050241]
#
#     db_loader = DBLoader(feed, start_time=datetime(2018, 1, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
#                          end_time=datetime(2018, 3, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
#                          symbol_ids=symbol_ids, timeframe=4, compression=5)
#
#     db_loader.load_data()


# __main__()

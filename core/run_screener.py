from dateutil.tz import tzoffset

from brokers.test_broker import TestBroker
from brokers.zerodha_broker import ZerodhaBroker
from brokers.alpha_broker import AlphaBroker
from core.tejas_run_modes import TejasRunModes
from feeds.db_loader import DBLoader
from feeds.zerodhafeed import ZerodhaFeed
from feeds.mongofeed import MongoFeed
from core.tejas import Tejas
from screeners.screener import Screener
from screeners.screener_builder import ScreenerBuilder
from strategies.strategy_builder import StrategyBuilder
from technicals.technical import *
from utils import my_constants as mconst
from datetime import datetime

stocks = ["ACC", "ADANIENT", "ADANIPORTS", "ADANIPOWER", "AMARAJABAT", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE",
          "ASHOKLEY", "ASIANPAINT", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND",
          "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON",
          "BOSCHLTD", "BPCL", "BRITANNIA", "CADILAHC", "CANBK", "CENTURYTEX", "CESC", "CHOLAFIN", "CIPLA", "COALINDIA",
          "COLPAL", "CONCOR", "CUMMINSIND", "DABUR", "DIVISLAB", "DLF", "DRREDDY", "EICHERMOT", "EQUITAS", "ESCORTS",
          "EXIDEIND", "FEDERALBNK", "GAIL", "GLENMARK", "GMRINFRA", "GODREJCP", "GODREJPROP", "GRASIM", "HAVELLS",
          "HCLTECH", "HDFC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDPETRO", "HINDUNILVR", "IBULHSGFIN",
          "ICICIBANK", "ICICIPRULI", "IDEA", "IDFCFIRSTB", "IGL", "INDIGO", "INDUSINDBK", "INFRATEL", "INFY", "IOC",
          "ITC", "JINDALSTEL", "JSWSTEEL", "JUBLFOOD", "JUSTDIAL", "KOTAKBANK", "L&TFH", "LICHSGFIN", "LT", "LUPIN",
          "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCDOWELL-N", "MFSL", "MGL", "MINDTREE", "MOTHERSUMI",
          "MRF", "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NCC", "NESTLEIND", "NIITTECH", "NMDC", "NTPC", "ONGC",
          "PAGEIND", "PEL", "PETRONET", "PFC", "PIDILITIND", "PNB", "POWERGRID", "PVR", "RAMCOCEM", "RBLBANK", "RECLTD",
          "RELIANCE", "SAIL", "SBIN", "SHREECEM", "SIEMENS", "SRF", "SRTRANSFIN", "SUNPHARMA", "SUNTV", "TATACHEM",
          "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TORNTPOWER",
          "TVSMOTOR", "UBL", "UJJIVAN", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "YESBANK", "ZEEL"]


def __main__():
    # feed = ZerodhaFeed(broker=None)
    feed = MongoFeed(broker=None)
    tejas = Tejas(feed=feed, mode=TejasRunModes.BACKTEST, plot=True)
    # broker = ZerodhaBroker(uid=mconst.UID)
    broker = TestBroker()
    tejas.set_broker(broker)
    feed.set_broker(broker)

    # tejas.add_screener(Screener(position="BUY", name="Test_Name",
    #          symbol_ids=stocks, start_time=datetime(2020, 1, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
    #                                                  end_time=datetime(2020, 5, 12, 12, 9,
    #                                                                    tzinfo=tzoffset(None, 19800)),
    #                                                  timeframe=5,
    #                                                  compression=1, feed=feed))
    tejas.add_screener(ScreenerBuilder(feed, screener_name="RSI Divergence Long", symbol_ids=stocks,
                                       start_time=datetime(2020, 1, 1, 0, 0, tzinfo=tzoffset(None, 19800)),
                                       end_time=datetime(2020, 5, 12, 12, 9, tzinfo=tzoffset(None, 19800))))

    tejas.screen()


__main__()

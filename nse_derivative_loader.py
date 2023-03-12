import math

from nsepy import get_history, derivatives, history
from datetime import date, datetime, timedelta
import pandas as pd
from nsepy.commons import unzip_str
from nsepy.urls import URLFetchSession
# from requests.packages.urllib3.packages import six

import model as md
import requests
from termcolor import colored

from utils import my_constants

import sys
sys.path.append('..')
from core.option_chain_analyzer import OptionChainAnalyzer as oca

position_priority_dict = {
    "Not Decided": 0,
    "Strong Long": 1,
    "Strong Short": 2,
    "Long": 2.4,
    "Short": 2.8,
    "Short Covering": 3,
    "Long Covering": 4,
    "New Longs": 5,
    "New Shorts": 6,
    "Long Last Leg": 7,
    "Short Last Leg": 8,
    "Weaker Longs": 9,
    "Weaker Shorts": 10,
    "Weak Short Covering": 11,
    "Weak Long Covering": 12,
    "No Long Position": 13,
    "No Short Position": 14,
    "No Interest": 15
}

derivative_price_list_url = URLFetchSession(
    url='https://archives.nseindia.com/content/historical/DERIVATIVES/%s/%s/fo%sbhav.csv.zip'
)

eq_price_delivery_list_url = URLFetchSession(
    url='https://archives.nseindia.com/products/content/sec_bhavdata_full_%s.csv'
)

oi_date = datetime.now()
index_bhav_copy = pd.DataFrame()

# stocks = ["BANDHANBNK"]

stocks = ["ACC", "ADANIENT", "ADANIPORTS", "AMARAJABAT", "AMBUJACEM", "APOLLOHOSP", "APOLLOTYRE",
          "ASHOKLEY", "ASIANPAINT", "AUROPHARMA", "AXISBANK", "BAJAJ-AUTO", "BAJAJFINSV", "BAJFINANCE", "BALKRISIND",
          "BANDHANBNK", "BANKBARODA", "BATAINDIA", "BEL", "BERGEPAINT", "BHARATFORG", "BHARTIARTL", "BHEL", "BIOCON",
          "BPCL", "BRITANNIA", "CADILAHC", "CANBK", "CENTURYTEX", "CHOLAFIN", "CIPLA", "COALINDIA",
          "COLPAL", "CONCOR", "CUMMINSIND", "DABUR", "DIVISLAB", "DLF", "DRREDDY", "EICHERMOT", "EQUITAS", "ESCORTS",
          "EXIDEIND", "FEDERALBNK", "GAIL", "GLENMARK", "GMRINFRA", "GODREJCP", "GODREJPROP", "GRASIM", "HAVELLS",
          "HCLTECH", "HDFC", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDPETRO", "HINDUNILVR", "IBULHSGFIN",
          "ICICIBANK", "ICICIPRULI", "IDEA", "IDFCFIRSTB", "IGL", "INDIGO", "INDUSINDBK", "INFRATEL", "INFY", "IOC",
          "ITC", "JINDALSTEL", "JSWSTEEL", "JUBLFOOD", "KOTAKBANK", "L&TFH", "LICHSGFIN", "LT", "LUPIN",
          "M&M", "M&MFIN", "MANAPPURAM", "MARICO", "MARUTI", "MCDOWELL-N", "MFSL", "MGL", "MINDTREE", "MOTHERSUMI",
          "MUTHOOTFIN", "NATIONALUM", "NAUKRI", "NESTLEIND", "NIITTECH", "NMDC", "NTPC", "ONGC",
          "PAGEIND", "PEL", "PETRONET", "PFC", "PIDILITIND", "PNB", "POWERGRID", "RAMCOCEM", "RBLBANK", "RECLTD",
          "RELIANCE", "SAIL", "SBIN", "SHREECEM", "SIEMENS", "SRF", "SRTRANSFIN", "SUNPHARMA", "SUNTV", "TATACHEM",
          "TATACONSUM", "TATAMOTORS", "TATAPOWER", "TATASTEEL", "TCS", "TECHM", "TITAN", "TORNTPHARM", "TORNTPOWER",
          "TVSMOTOR", "UBL", "UJJIVAN", "ULTRACEMCO", "UPL", "VEDL", "VOLTAS", "WIPRO", "ZEEL"]

indices = ["NIFTY", "BANKNIFTY"]


end = datetime.now()
start = end - timedelta(days=90)
final_df = pd.DataFrame(columns={'close', 'low', 'open', 'high', 'vwap', 'delivery', 'stock',
                                 'price_change', 'avg_del', 'delivery_change', 'oi_combined', 'coi_change'})

current_month = datetime.now().month
next_month = current_month % 12 + 1

current_month_year = datetime.now().year
next_month_year = current_month_year + 1 if next_month == 1 else current_month_year


def update_position_priority():
    results = get_mongo_data(sort_order=1)

    for result in results:
        try:
            if result['stock'] in indices:
                priority, position = 0, "Not Decided"
            else:
                stock_detail = {
                    "net_ce_change": result['net_ce_change'],
                    "net_pe_change": result['net_pe_change'],
                    "pcr": result['pcr'],
                    "price_change": result['change_list'][0]['price_change'],
                    "coi_change": result['change_list'][0]['coi_change'],
                    "delivery_change": result['change_list'][0]['delivery_change']
                }
                temp_df = pd.DataFrame(result['change_list'])
                low_price_change = temp_df.price_change[temp_df.price_change < 0].mean()
                high_price_change = temp_df.price_change[temp_df.price_change > 0].mean()
                delivery_change = temp_df.delivery_change.mean()
                low_coi_change = temp_df.coi_change[temp_df.coi_change < 0].mean()
                high_coi_change = temp_df.coi_change[temp_df.coi_change > 0].mean()

                print(f"Finding position for {result['stock']}")

                priority, position = conditions(stock_detail, low_price_change, high_price_change,
                                                    delivery_change, low_coi_change, high_coi_change)

            md.pmdb["DerivativeAnalysisResult"].update(
                {
                    "$and": [
                        {"stock": result['stock']},
                        {"datetime": result['datetime']}
                    ]
                },
                {
                    "$set": {
                        "priority": priority,
                        "position": position
                    }
                })
            print(f"Updated {result['stock']} with priority {priority} and position {position}")
        except Exception as ex:
            print(ex)
            print(colored(f"Error occured while ranking {result['stock']}", 'red'))


def getPosition(rank):
    if rank > 120:
        return "Strong Long"
    elif 80 < rank <= 120:
        return "Long"
    elif 40 < rank <= 80:
        return "Weeker Long"
    if rank < -120:
        return "Strong Short"
    elif -80 > rank >= -120:
        return "Short"
    elif -40 > rank >= -80:
        return "Weeker Short"
    else:
        return "No Interest"


def fetch_historical_stock_data(stock, start_date, end_date=datetime.now()):
    data = get_history(symbol=stock, start=start_date, end=end_date)
    final_df['close'] = data['Close']
    final_df['low'] = data.Low
    final_df['open'] = data.Open
    final_df['high'] = data.High
    final_df['vwap'] = data.VWAP
    final_df['delivery'] = data['Turnover'] * data['%Deliverble'] / 100000000000
    final_df['price_change'] = (data['Close'] - data['Prev Close'])*100/data['Close']
    final_df['avg_del'] = final_df['delivery'].rolling(5, min_periods=0).mean().shift().bfill()
    # final_df['avg_del'] = final_df['delivery'].apply(lambda x: x.rolling(5, min_periods=1).mean().shift().bfill())
    final_df['delivery_change'] = final_df['delivery'] * 100 / final_df['avg_del']
    final_df['stock'] = stock
    if final_df.shape[0] + 1 == data.shape[0]:
        final_df['datetime'] = pd.to_datetime(data.index)[0:-1]
    else:
        final_df['datetime'] = pd.to_datetime(data.index)
    return final_df


def fetch_historical_futures_data(stock, start_date, end_date=datetime.now(), is_stock=True):
    expiry_month = start_date.month
    expiry_year = end_date.year
    oi_combined_series = pd.Series()
    index_df = pd.DataFrame(columns=["Symbol", "Expiry", "Open", "High", "Low", "Close", "Last", "Settle Price",
                                     "Number of Contracts", "Turnover", "Open Interest", "Change in OI",
                                     "Underlying", "Open Interest2"])
    while True:
        if start_date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            break
        n_month, n_year = get_next_month_year(expiry_month, expiry_year)

        try:
            current_month_expiry = get_expiry_date(expiry_month, expiry_year, is_stock)
            current_month_expiry = sorted(current_month_expiry, reverse=True)
            if datetime.date(start_date) > current_month_expiry[0]:
                expiry_month, expiry_year = n_month, n_year
                n_month, n_year = get_next_month_year(expiry_month, expiry_year)
                current_month_expiry = get_expiry_date(expiry_month, expiry_year, is_stock)
                current_month_expiry = sorted(current_month_expiry, reverse=True)

            next_month_expiry = get_expiry_date(n_month, n_year, is_stock)
            next_month_expiry = sorted(next_month_expiry, reverse=True)

            expiry_month, expiry_year = n_month, n_year
            end = datetime(year=list(current_month_expiry)[0].year,
                           month=list(current_month_expiry)[0].month, day=list(current_month_expiry)[0].day)

            data_fut = get_history(symbol=stock, index=not is_stock, futures=True, start=start_date, end=end,
                                   expiry_date=list(current_month_expiry)[0])
            data_fut2 = get_history(symbol=stock, index=not is_stock, futures=True, start=start_date, end=end,
                                    expiry_date=list(next_month_expiry)[0])
        except Exception as e:
            print(e)

        if is_stock:
            oi_combined = pd.concat([data_fut2['Open Interest'], data_fut['Open Interest']],
                                    axis=1)
            oi_combined_series = oi_combined_series.append(oi_combined.sum(axis=1))
        else:
            temp_df = pd.concat([data_fut, data_fut2['Open Interest'].rename("Open Interest2")],
                                axis=1)
            index_df = index_df.append(temp_df)

        start_date = end + timedelta(days=1)

    if not is_stock:
        index_df['Open Interest2'].ffill(0, inplace=True)
        index_df['oi_combined'] = index_df['Open Interest'] + index_df['Open Interest2']
        index_df['coi_change'] = index_df.oi_combined.pct_change() * 100
        return index_df

    final_df['oi_combined'] = oi_combined_series
    final_df['coi_change'] = final_df.oi_combined.pct_change() * 100
    return final_df


def get_derivativeprice_list(dt, price_type="fo"):
    MMM = dt.strftime("%b").upper()
    yyyy = dt.strftime("%Y")
    if price_type == "eq":
        fp = eq_price_delivery_list_url(dt.strftime("%d") + dt.strftime("%m") + dt.strftime("%Y"))
        txt = fp.content.decode("utf-8")
        txt = txt.replace(" ", "")
    else:
        res = derivative_price_list_url(yyyy, MMM, dt.strftime("%d%b%Y").upper())
        txt = unzip_str(res.content)
    # fp = six.StringIO(txt)
    df = pd.read_csv(txt)
    return df


def get_daily_fo_bhav_copy(bhavcopy_dt, is_index=False):
    dbhav = get_derivativeprice_list(dt=bhavcopy_dt)
    if is_index:
        derivative_df = dbhav[dbhav.INSTRUMENT == 'FUTIDX'][
            dbhav[dbhav.INSTRUMENT == 'FUTIDX'].EXPIRY_DT != dbhav['EXPIRY_DT'][2]]
        derivative_df.drop(["INSTRUMENT", "EXPIRY_DT", "STRIKE_PR", "OPTION_TYP", "SETTLE_PR",
                            "CONTRACTS", "VAL_INLAKH", "CHG_IN_OI", "Unnamed: 15"], axis=1, inplace=True)

    else:
        derivative_df = dbhav[dbhav.INSTRUMENT == 'FUTSTK'][
            dbhav[dbhav.INSTRUMENT == 'FUTSTK'].EXPIRY_DT != dbhav['EXPIRY_DT'][2]]
        derivative_df.drop(["INSTRUMENT", "EXPIRY_DT", "STRIKE_PR", "OPTION_TYP", "OPEN", "HIGH", "LOW",
                            "CLOSE", "SETTLE_PR", "CONTRACTS", "VAL_INLAKH", "CHG_IN_OI", "Unnamed: 15"]
                           , axis=1, inplace=True)

    derivative_df['oi_combined'] = derivative_df.groupby("SYMBOL")["OPEN_INT"].transform("sum")
    derivative_df.drop_duplicates(subset="SYMBOL", inplace=True, ignore_index=True)
    derivative_df = derivative_df.drop("OPEN_INT", axis=1)
    return derivative_df


def get_daily_eq_bhav_copy(bhavcopy_dt):
    dbhav = get_derivativeprice_list(dt=bhavcopy_dt, price_type="eq")
    eq_df = dbhav[dbhav.SERIES == 'EQ']
    eq_df = eq_df.drop(["SERIES", "LAST_PRICE"], axis=1)
    eq_df['price_change'] = (eq_df['CLOSE_PRICE'] - eq_df['PREV_CLOSE']) * 100 / eq_df['PREV_CLOSE']
    eq_df['delivery'] = eq_df['TURNOVER_LACS'] * eq_df['DELIV_PER'].astype("float") / 1000
    return eq_df


def get_dates_to_fetch(stock):
    result = md.pmdb['DerivativeAnalysisResult'].find({"stock": stock}).sort([("datetime", -1)]).limit(1)
    data_exists = True
    result = list(result)
    if len(result) > 0:
        s_date = result[0]['datetime'] + timedelta(days=1)
        if s_date.strftime("%A") == "Saturday":
            s_date = result[0]['datetime'] + timedelta(days=2)
        elif s_date.strftime("%A") == "Sunday":
            s_date = result[0]['datetime'] + timedelta(days=1)
    else:
        s_date = datetime.now() - timedelta(days=100)
        data_exists = False
    return s_date, datetime.now(), data_exists
    # data = get_history(symbol=result[0]['stock'], start=s_date, end=e_date)
    # print(data)


def conditions(df, low_price_change=-5, high_price_change=5,
               delivery_change=100, low_coi_change=-5, high_coi_change=5):

    if df['net_pe_change'] > 0 and df['net_ce_change'] < 0:
        position = "Long"
    elif df['net_pe_change'] < 0 and df['net_ce_change'] > 0:
        position = "Short"

    delivery_change = 99;
    low_coi_change = -4;
    high_coi_change = -4;
    # Case of Rising Prices
    if df['price_change'] > high_price_change and df['delivery_change'] > delivery_change \
            and df['coi_change'] > high_coi_change:
        position = "Strong Long"

    elif df['price_change'] > high_price_change and df['delivery_change'] < \
            delivery_change and df['coi_change'] > high_coi_change:
        position = "New Longs"

    elif df['price_change'] > high_price_change and df['delivery_change'] < delivery_change / 2 \
            and df['coi_change'] > low_coi_change:
        position = "Weaker Longs"

    elif df['price_change'] > high_price_change and df['delivery_change'] > \
            delivery_change and low_coi_change < df['coi_change'] < high_coi_change:
        position = "Long Last Leg"

    elif df['price_change'] > high_price_change and df['delivery_change'] < delivery_change / 2 and \
            low_coi_change < df['coi_change'] < high_coi_change:
        position = "No Long Position"

    elif df['price_change'] > high_price_change and df['delivery_change'] > delivery_change and \
            df['coi_change'] < low_coi_change:
        position = "Short Covering"

    elif df['price_change'] > high_price_change and df['delivery_change'] < delivery_change and \
            df['coi_change'] < low_coi_change:
        position = "Weak Short Covering"

    # Case of Falling Prices
    elif df['price_change'] < low_price_change and df['delivery_change'] > delivery_change \
            and df['coi_change'] > high_coi_change:
        position = "Strong Short"

    elif df['price_change'] < low_price_change and df['delivery_change'] < \
            delivery_change and df['coi_change'] > high_coi_change:
        position = "New Shorts"

    elif df['price_change'] < low_price_change and df['delivery_change'] < delivery_change * 0.75 \
            and df['coi_change'] > low_coi_change:
        position = "Weaker Shorts"

    elif df['price_change'] < low_price_change and df['delivery_change'] > \
            delivery_change and low_coi_change < df['coi_change'] < high_coi_change:
        position = "Short Last Leg"

    elif df['price_change'] < low_price_change and df['delivery_change'] < delivery_change * 0.75 and \
            low_coi_change < df['coi_change'] < high_coi_change:
        position = "No Short Position"

    elif df['price_change'] < low_price_change and df['delivery_change'] > delivery_change and \
            df['coi_change'] < low_coi_change:
        position = "Long Covering"

    elif df['price_change'] < low_price_change and df['delivery_change'] < delivery_change * 0.75 and \
            df['coi_change'] < low_coi_change:
        position = "Weak Long Covering"

    else:
        position = "No Interest"

    return position_priority_dict[position], position


def set_priority(df):
    return position_priority_dict[df['position']]


def get_next_month_year(month, year, fwd_month=1):
    if fwd_month == 2:
        if month < 11:
            n_month = month + 2
        elif month == 11:
            n_month = 1
        elif month == 12:
            n_month = 2
        n_year = year + 1 if n_month == 1 or n_month == 2 else year
    else:
        n_month = month % 12 + 1
        n_year = year + 1 if n_month == 1 else year
    return n_month, n_year


def load_initial_data(instrument, s_date, e_date=datetime.now()):
    records = list(md.pmdb['DerivativeAnalysisResult'].find({'stock': instrument}))
    try:
        if len(records) == 0:
            fetch_historical_stock_data(instrument, s_date, e_date)
            if final_df.shape[0] > 0:
                fetch_historical_futures_data(instrument, s_date, e_date)
            else:
                return
            final_df.round(2)
            md.pmdb['DerivativeAnalysisResult'].insert_many(final_df.to_dict('records'))
            print("Data inserted for " + instrument)
        else:
            print("Already data exist for " + instrument)
    except Exception as ex:
        print(ex)


def get_mongo_data(record_count=100, sort_order=-1):
    result = list(md.pmdb['DerivativeAnalysisResult'].aggregate([
        {'$sort': {'datetime': sort_order}},
        {'$group': {
            "_id": "$stock",
            "stock": {'$last': '$stock'},
            'datetime': {'$last': '$datetime'},
            'oi_combined': {"$last": "$oi_combined"},
            'vwap': {"$last": "$vwap"},
            'net_ce_change': {"$last": "$net_ce_change"},
            'net_pe_change': {"$last": "$net_pe_change"},
            'pcr': {"$last": "$pcr"},
            'delivery_list': {"$push": {"delivery": "$delivery"}},
            'change_list': {"$push": {"delivery_change": "$delivery_change",
                                      "price_change": "$price_change",
                                      "coi_change": "$coi_change"}},
        }
        },
        {
            '$project': {
                "datetime": "$datetime",
                "stock": "$stock",
                "oi_combined": "$oi_combined",
                "delivery_list": {"$slice": ["$delivery_list", my_constants.DAYS_FOR_AVG_DELIVERY]},
                'vwap': "$vwap",
                'net_ce_change': "$net_ce_change",
                'net_pe_change': "$net_pe_change",
                'pcr': "$pcr",
                "change_list": {"$slice": [{"$reverseArray": "$change_list"}, my_constants.DAYS_FOR_CHANGE_MEAN]}
            }
        },
        {
            '$project': {
                "datetime": "$datetime",
                "stock": "$stock",
                "oi_combined": "$oi_combined",
                "avg_del": {"$avg": "$delivery_list.delivery"},
                'vwap': "$vwap",
                'net_ce_change': "$net_ce_change",
                'net_pe_change': "$net_pe_change",
                'pcr': "$pcr",
                "change_list": "$change_list"
            }
        },
    ]))
    return list(result)


def prepare_left_historical_data(stock, s_date, e_date):
    db_data = list(md.pmdb['DerivativeAnalysisResult'].find({"stock": stock}).sort([("datetime", 1)]).limit(90))
    db_df = pd.DataFrame(db_data)
    fetch_historical_stock_data(stock=stock, start_date=s_date, end_date=e_date)
    if final_df.shape[0] == 0:
        return
    else:
        df = fetch_historical_futures_data(stock=stock, start_date=s_date, end_date=e_date)
        df['datetime'] = pd.to_datetime(df.index)
        db_df.drop(columns=["_id"], axis=1, inplace=True)
        prev_row_count = db_df.shape[0]

    if df.shape[0] > 0:
        db_df = db_df.append(df, ignore_index=True)
        db_df['price_change'] = db_df.close.pct_change() * 100
        # db_df['avg_del'] = db_df['delivery'].rolling(5, min_periods=0).mean()
        db_df['avg_del'] = db_df['delivery'].rolling(5, min_periods=1).mean().shift().bfill()
        db_df['delivery_change'] = db_df['delivery'] * 100 / db_df['avg_del']
        db_df['coi_change'] = db_df.oi_combined.pct_change() * 100
        db_df.round(2)

        db_df = db_df.loc[prev_row_count:, :]
        md.pmdb['DerivativeAnalysisResult'].insert_many(db_df.to_dict('records'))
        print("Data inserted for " + stock)
    else:
        print("No new data available to insert for " + stock)


def get_bhavcopy_date():
    curr_datetime = datetime.now()
    if curr_datetime.hour >= 19:
        bhavcopy_date = date.today()
    else:
        bhavcopy_date = date.today() - timedelta(days=1)

    if bhavcopy_date.strftime("%A") == "Saturday":
        bhavcopy_date = bhavcopy_date - timedelta(days=1)
    elif bhavcopy_date.strftime("%A") == "Sunday":
        bhavcopy_date = bhavcopy_date - timedelta(days=2)

    return bhavcopy_date


# Daily Loading
def load_daily_bhav_copy():
    bhavcopy_date = get_bhavcopy_date()
    try:
        eq_df = get_daily_eq_bhav_copy(bhavcopy_date)
    except:
        bhavcopy_date = bhavcopy_date - timedelta(days=1)
        eq_df = get_daily_eq_bhav_copy(bhavcopy_date)

    der_df = get_daily_fo_bhav_copy(bhavcopy_date)
    bhavcopy = pd.merge(der_df, eq_df, on="SYMBOL", right_index=True)
    bhavcopy.rename(columns={'SYMBOL': 'stock', 'OPEN_PRICE': 'open', 'CLOSE_PRICE': 'close', 'LOW_PRICE': 'low',
                             'HIGH_PRICE': 'high', 'AVG_PRICE': 'vwap', 'TIMESTAMP': 'datetime'}, inplace=True)

    bhavcopy.drop(columns=['DATE1', 'DELIV_PER', 'DELIV_QTY', 'NO_OF_TRADES',
                           'PREV_CLOSE', 'TTL_TRD_QNTY', 'TURNOVER_LACS'], inplace=True)
    bhavcopy['datetime'] = pd.to_datetime(bhavcopy['datetime'])
    # md.pmdb['DerivativeAnalysisResult'].insert_many(bhavcopy.to_dict('records'))
    # print("Data updated to database successfully")
    return bhavcopy


# Update db with option data
def update_option_data(stocks, type="equities"):
    for ticker in stocks:
        db_data = list(md.pmdb['DerivativeAnalysisResult'].find({"stock": ticker}).sort("datetime", -1).limit(2))
        result = oca.fetch_oi(stock=ticker, type=type)
        if result is None:
            result = md.pmdb["DerivativeAnalysisResult"].update(
                {
                    "$and": [
                        {"stock": ticker},
                        {"datetime": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
                    ]
                },
                {
                    "$set": {
                        "oi_combined": 0,
                        "max_pain_pe": {},
                        "max_pain_ce": {},
                        "net_ce": 0,
                        "net_pe": 0,
                        "net_ce_change": 0,
                        "net_pe_change": 0,
                        "net_ce_change_pct": 0,
                        "net_pe_change_pct": 0,
                        "pcr": 1,
                        "pcr_of_change": 0
                    }
                })
        else:
            if "net_ce" not in db_data[0].keys() or db_data[0]['net_ce'] == 0 or math.isnan(db_data[0]['net_ce']):
                net_ce_change = 0
                net_ce_change_pct = 0
            else:
                net_ce_change = result['net_ce'] - db_data[0]['net_ce']
                net_ce_change_pct = (result['net_ce'] - db_data[0]['net_ce']) * 100 / db_data[0]['net_ce']

            if "net_pe" not in db_data[0].keys() or db_data[0]['net_pe'] == 0 or math.isnan(db_data[0]['net_pe']):
                net_pe_change = 0
                net_pe_change_pct = 0
            else:
                net_pe_change = result['net_pe'] - db_data[0]['net_pe']
                net_pe_change_pct = (result['net_pe'] - db_data[0]['net_pe']) * 100 / db_data[0]['net_pe']

            if "net_pe" in db_data[0].keys() \
                    and "net_pe" in db_data[0].keys() \
                    and (result['net_ce'] - db_data[0]['net_ce']) != 0 \
                    and not math.isnan(db_data[0]['net_ce'])\
                    and not math.isnan(db_data[0]['net_pe']):
                pcr_of_change = (result['net_pe'] - db_data[0]['net_pe']) * 100 / (result['net_ce'] - db_data[0]['net_ce'])
            else:
                pcr_of_change = 0
                pcr = 99

            temp = datetime.strptime(result['datetime'], "%d-%b-%Y %H:%M:%S") \
                .replace(hour=0, minute=0, second=0, microsecond=0)
            try:
                result = md.pmdb["DerivativeAnalysisResult"].update(
                    {
                        "$and": [
                            {"stock": ticker},
                            {"datetime": temp}
                        ]
                    },
                    {
                        "$set": {
                            "max_pain_pe": result['max_pain_pe'],
                            "max_pain_ce": result['max_pain_ce'],
                            "net_ce": int(result['net_ce']),
                            "net_pe": int(result['net_pe']),
                            "net_ce_change": float(net_ce_change),
                            "net_pe_change": float(net_pe_change),
                            "net_ce_change_pct": float(net_ce_change_pct),
                            "net_pe_change_pct": float(net_pe_change_pct),
                            "pcr": float(result["pcr"]),
                            "pcr_of_change": float(pcr_of_change)
                        }
                    })
                print(f"{result['nModified']} option data records were updated for {ticker}")
            except Exception as e:
                print(colored(e, "red"))


# Steps for loading data
# 1. Check if data exists in database
# 2. If it does not exist call historical and load data from specified number of days in past
# 3. If it exist then check the last date and fill the data if some days are missing
# 4. If data is full then check for bhavcopy and update it in database

def update_stock_data():
    for stock in stocks:
        s_date, e_date, data_exists = get_dates_to_fetch(stock)
        try:
            if s_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                if not data_exists:
                    load_initial_data(stock, s_date, e_date)
                else:
                    prepare_left_historical_data(stock, s_date=s_date, e_date=e_date)
            else:
                print(colored("Data is present till previous trading session for " + stock, "green"))
        except Exception as ex:
            print(colored(ex, "red"))
            print("Error occured for " + stock)

    bhavcopy = load_daily_bhav_copy()
    bhavcopy = bhavcopy[bhavcopy.stock.isin(stocks)]
    bhavcopy.reset_index(inplace=True, drop=True)
    results = get_mongo_data(sort_order=1)
    db_stock_list = []
    for result in results:
        db_stock_list.append(result['stock'])
        try:
            if result['datetime'] >= bhavcopy['datetime'][0]:
                bhavcopy = bhavcopy[bhavcopy.stock != result['stock']]
                bhavcopy.reset_index(inplace=True, drop=True)
            else:
                bhavcopy.loc[bhavcopy.stock == result['stock'], 'avg_del'] = result['avg_del']
                bhavcopy.loc[bhavcopy.stock == result['stock'], 'delivery_change'] = \
                    bhavcopy.loc[bhavcopy.stock == result['stock'], 'delivery'] * 100 / result['avg_del']
                bhavcopy.loc[bhavcopy.stock == result['stock'], 'coi_change'] = \
                    (bhavcopy.loc[bhavcopy.stock == result['stock'], 'oi_combined'] - result['oi_combined']) * 100 / \
                    result['oi_combined']
        except Exception as e:
            print(e)
            print("Error occured while processing bhavcopy for " + result['stock'])

    bhavcopy = bhavcopy[bhavcopy.stock.isin(db_stock_list)]
    bhavcopy.reset_index(inplace=True, drop=True)
    if bhavcopy.shape[0] > 0:
        md.pmdb['DerivativeAnalysisResult'].insert_many(bhavcopy.to_dict('records'))
        print("Future data updated successfully")
    else:
        print("No new data available in bhavcopy")


def update_index_data():
    for index in indices:
        s_date, e_date, data_exists = get_dates_to_fetch(index)
        try:
            if s_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                if not data_exists:
                    df = fetch_historical_futures_data(index, s_date, e_date, is_stock=False)
                    df['datetime'] = pd.to_datetime(df.index)
                    df.rename(columns={"Symbol": "stock", "Open": "open", "High": "high", "Low": "low",
                                       "Close": "close"}, inplace=True)
                    df.drop(columns=["Expiry", "Last", "Settle Price", "Number of Contracts", "Turnover",
                                     "Open Interest", "Change in OI", "Underlying", "Open Interest2"], inplace=True)
                    md.pmdb['DerivativeAnalysisResult'].insert_many(df.to_dict('records'))
                else:
                    db_data = list(
                        md.pmdb['DerivativeAnalysisResult'].find({"stock": index}).sort([("datetime", 1)]).limit(90))
                    db_df = pd.DataFrame(db_data)
                    df = fetch_historical_futures_data(stock=index, start_date=s_date, end_date=e_date, is_stock=False)
                    df.rename(columns={"Symbol": "stock", "Open": "open", "High": "high", "Low": "low",
                                       "Close": "close"}, inplace=True)
                    df.drop(columns=["Expiry", "Last", "Settle Price", "Number of Contracts", "Turnover",
                                     "Open Interest", "Change in OI", "Underlying", "Open Interest2"], inplace=True)
                    df['datetime'] = pd.to_datetime(df.index)
                    db_df.drop(columns=["_id"], axis=1, inplace=True)
                    prev_row_count = db_df.shape[0]

                    if df.shape[0] > 0:
                        db_df = db_df.append(df, ignore_index=True)
                        db_df['price_change'] = db_df.close.pct_change() * 100
                        db_df['coi_change'] = db_df.oi_combined.pct_change() * 100
                        db_df.round(2)

                        db_df = db_df.loc[prev_row_count:, :]
                        md.pmdb['DerivativeAnalysisResult'].insert_many(db_df.to_dict('records'))
                        print("Data inserted for " + index)
                    else:
                        print("No new data available to insert for " + index)
            else:
                print("Data is present till previous trading session for " + index)
        except Exception as ex:
            print(colored(ex, "red"))
            print("Error occured for " + index)

    bhavcopy_date = get_bhavcopy_date()
    # dbhav = get_derivativeprice_list(dt=bhavcopy_date)
    bhavcopy = get_daily_fo_bhav_copy(bhavcopy_date, is_index=True)

    bhavcopy.rename(columns={"SYMBOL": "stock", "OPEN": "open", "HIGH": "high", "LOW": "low",
                             "CLOSE": "close", "OPEN_INT": "oi", "TIMESTAMP": "datetime"}, inplace=True)

    bhavcopy['datetime'] = pd.to_datetime(bhavcopy['datetime'])
    bhavcopy = bhavcopy[bhavcopy.stock.isin(indices)]
    bhavcopy.reset_index(inplace=True, drop=True)
    results = get_mongo_data()
    db_stock_list = []
    for result in results:
        if bhavcopy.shape[0] == 0:
            break
        db_stock_list.append(result['stock'])
        try:
            if result['datetime'] >= bhavcopy['datetime'][0]:
                bhavcopy = bhavcopy[bhavcopy.stock != result['stock']]
                bhavcopy.reset_index(inplace=True, drop=True)
            else:
                bhavcopy.loc[bhavcopy.stock == result['stock'], 'coi_change'] = \
                    (bhavcopy.loc[bhavcopy.stock == result['stock'], 'oi_combined'] - result['oi_combined']) * 100 / \
                    result['oi_combined']
        except Exception as e:
            print(colored(e, "red"))
            print("Error occured while processing bhavcopy for " + result['stock'])

    bhavcopy = bhavcopy[bhavcopy.stock.isin(db_stock_list)]
    bhavcopy.reset_index(inplace=True, drop=True)
    if bhavcopy.shape[0] > 0:
        md.pmdb['DerivativeAnalysisResult'].insert_many(bhavcopy.to_dict('records'))
        print("Future data updated successfully")
    else:
        print("No new data available in bhavcopy")


def load_expiry_dates():
    r = requests.get("https://www.nseindia.com/api/quote-derivative?symbol=NIFTY",
                     timeout=15,
                     headers={'User-Agent': 'Mozilla/5.0'}).json()
    db_dates = list(md.pmdb["ExpiryDates"].find())
    db_dates = list(map(lambda el: el['expiryDate'], db_dates))
    res = []
    for i in r['expiryDates']:
        if i not in res and i not in db_dates:
            res.append(i)
            md.pmdb["ExpiryDates"].insert({'expiryDate': i})

    print(db_dates)


def get_expiry_date(expiry_month, expiry_year, is_stock=True, is_second_call=False):
    try:
        if expiry_year <= datetime.now().year or expiry_month <= datetime.now().month:
            return derivatives.get_expiry_date(
                expiry_year, expiry_month, index=not is_stock, stock=is_stock)
    except:
        ...

    month_dict = {"1": "Jan", "2": "Feb", "3": "Mar", "4": "Apr", "5": "May", "6": "Jun", "7": "Jul",
                  "8": "Aug", "9": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
                  }

    db_dates = list(md.pmdb["ExpiryDates"].find())
    db_dates = list(map(lambda el: el['expiryDate'], db_dates))
    temp = month_dict[str(expiry_month)] + "-" + str(expiry_year)
    res = []
    for i in db_dates:
        if temp in i:
            res.append(datetime.date(datetime.strptime(i, "%d-%b-%Y")))

    if len(res) > 0:
        return res
    elif is_second_call:
        return []
    else:
        load_expiry_dates()
        return get_expiry_date(expiry_month, expiry_year, is_stock, is_second_call=True)


def load_option_data_from_db():
    stocks.extend(indices)
    for ticker in stocks:
        try:
            results = list(md.pmdb["OptionData"].find({"stock": ticker}).sort("datetime", -1))
            for i in range(len(results)-1):
                result = results[i]
                final_dict = {
                    'max_pain_ce': result['max_pain_ce'],
                    'max_pain_pe': result['max_pain_pe'],
                    'net_ce': result['net_ce'],
                    'net_pe': result['net_pe'],
                    'pcr': result['pcr']
                }
                if i <= len(results)-2:
                    final_dict['net_ce_change'] = result['net_ce'] - results[i + 1]['net_ce']
                    final_dict['net_pe_change'] = result['net_pe'] - results[i + 1]['net_pe']
                    if results[i+1]['net_ce'] != 0:
                        final_dict['net_ce_change_pct'] = final_dict['net_ce_change']*100/results[i+1]['net_ce']
                    else:
                        final_dict['net_ce_change_pct'] = 99
                    if results[i + 1]['net_pe'] != 0:
                        final_dict['net_pe_change_pct'] = final_dict['net_pe_change']*100/results[i + 1]['net_pe']
                    else:
                        final_dict['net_pe_change_pct'] = 99

                    if final_dict['net_ce_change'] != 0:
                        final_dict['pcr_of_change'] = final_dict['net_pe_change']*100/final_dict['net_ce_change']
                    else:
                        final_dict['pcr_of_change'] = 1

                writeResult = md.pmdb['DerivativeAnalysisResult'].update({
                        "$and": [
                            {"stock": ticker},
                            {"datetime": result['datetime']}
                        ]
                    }, {"$set": final_dict}, False)
            print(f"Option loading completed for {ticker}")
        except Exception as ex:
            print(colored(f"Error occured for {ticker}", "red"))
            print(ex.with_traceback())


def calculate_pivots(data):
    pivot_points = {}
    pivot_points['bc'] = round((data['high'] + data['low']) / 2, 2)
    pivot_points['pivot'] = round((data['high'] + data['low'] + data['close']) / 3)
    pivot_points['tc'] = round(pivot_points['pivot'] * 2 - pivot_points['bc'])
    if pivot_points['bc'] > pivot_points['tc']:
        pivot_points['tc'], pivot_points['bc'] = pivot_points['bc'], pivot_points['tc']
    pivot_points['width'] = (pivot_points['tc'] - pivot_points['bc']) * 100 / pivot_points['pivot']

    pivot_points['s1'] = round(pivot_points['pivot'] * 2 - data['high'])
    pivot_points['s2'] = round(pivot_points['pivot'] - (data['high'] - data['low']))
    pivot_points['s3'] = round(pivot_points['pivot'] - (data['high'] - data['low'])*2)
    pivot_points['s4'] = round(pivot_points['s3'] - (pivot_points['s1'] - pivot_points['s2']))

    pivot_points['r1'] = round(pivot_points['pivot'] * 2 - data['low'])
    pivot_points['r2'] = round(pivot_points['pivot'] + (data['high'] - data['low']))
    pivot_points['r3'] = round(pivot_points['pivot'] + (data['high'] - data['low']) * 2)
    pivot_points['r4'] = round(pivot_points['r3'] + (pivot_points['r2'] - pivot_points['r1']))
    return pivot_points

def update_cpr():
    stocks.extend(indices)
    pivots = {"next": {}, "current": {}, "prev":{}}
    for ticker in stocks:
        results = list(md.pmdb["DerivativeAnalysisResult"].find({"stock": ticker}).sort("datetime", -1).limit(3))
        pivots["next"] = calculate_pivots(results[0])
        if "pivots" in results[1].keys() and results[1]['pivots']['next'] is not {}\
                and results[1]['pivots']['current'] is not {}:
            pivots['current'] = results[1]['pivots']['next']
            pivots['prev'] = calculate_pivots(results[2])
        else:
            pivots['current'] = calculate_pivots(results[1])
            pivots['prev'] = calculate_pivots(results[2])

        print(ticker)
        writeResult = md.pmdb["DerivativeAnalysisResult"].update(
            {"_id": results[0]['_id']},
            {"$set": {"pivot_points": pivots}}, False
        )
        print(writeResult)


def save_option_data_to_db():
    for ticker in stocks:
        try:
            oca.fetch_oi(stock=ticker, type="equities")
            print(f"Option data updated to db for {ticker}")
        except Exception as e:
            print(colored(e, "red"))
    for ticker in indices:
        try:
            oca.fetch_oi(stock=ticker, type="indices")
            print(f"Option data updated to db for {ticker}")
        except Exception as e:
            print(colored(e, "red"))


# update_stock_data()

# update_index_data()

# update_option_data(stocks, "equities")
# update_option_data(indices, "indices")

# load_option_data_from_db()
# save_option_data_to_db()

# update_cpr()

# update_position_priority()

def nse_derivative_loader_main():
    # print("Function called successfully")
    update_stock_data()

    update_index_data()

    update_option_data(stocks, "equities")
    update_option_data(indices, "indices")

    load_option_data_from_db()
    save_option_data_to_db()

    update_cpr()

    update_position_priority()

# nse_derivative_loader_main()
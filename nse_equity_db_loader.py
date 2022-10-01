from nsepy import get_history, derivatives, history
from datetime import date, datetime, timedelta
import pandas as pd
from nsepy.commons import unzip_str
from nsepy.urls import URLFetchSession
from requests.packages.urllib3.packages import six
import model as md
from core.option_chain_analyzer import OptionChainAnalyzer as oca
import numpy as np
import matplotlib.pyplot as plt

eq_price_delivery_list_url = URLFetchSession(
    url='https://archives.nseindia.com/products/content/sec_bhavdata_full_%s.csv'
)

# stocks = ["ACC"]

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


def fetch_historical_stock_data(stock, start_date, end_date=datetime.now()):
    final_df = pd.DataFrame()
    data = get_history(symbol=stock, start=start_date, end=end_date)
    final_df['close'] = data['Close']
    final_df['low'] = data.Low
    final_df['open'] = data.Open
    final_df['high'] = data.High
    final_df['vwap'] = data.VWAP
    final_df['delivery'] = data['Turnover'] * data['%Deliverble'] / 1000000000
    final_df['price_change'] = data.Close.pct_change() * 100
    final_df['avg_del'] = final_df['delivery'].rolling(5).mean()
    final_df['delivery_change'] = final_df['delivery'] * 100 / final_df['avg_del']
    final_df['stock'] = stock
    final_df['datetime'] = pd.to_datetime(data.index)
    return final_df


def get_derivativeprice_list(dt, price_type="fo"):
    fp = eq_price_delivery_list_url(dt.strftime("%d") + dt.strftime("%m") + dt.strftime("%Y"))
    txt = fp.content.decode("utf-8")
    txt = txt.replace(" ", "")
    fp = six.StringIO(txt)
    df = pd.read_csv(fp)
    return df


def get_daily_eq_bhav_copy(bhavcopy_dt):
    dbhav = get_derivativeprice_list(dt=bhavcopy_dt, price_type="eq")
    eq_df = dbhav[dbhav.SERIES == 'EQ']
    eq_df = eq_df.drop(["SERIES", "LAST_PRICE"], axis=1)
    eq_df['price_change'] = (eq_df['CLOSE_PRICE'] - eq_df['PREV_CLOSE']) * 100 / eq_df['PREV_CLOSE']
    eq_df['delivery'] = eq_df['TURNOVER_LACS'] * eq_df['DELIV_PER'].astype("float") / 1000
    return eq_df


def get_dates_to_fetch(stock):
    result = md.pmdb['HistoricalData'].find({"stock": stock}).sort([("datetime", -1)]).limit(1)
    data_exists = True
    result = list(result)
    if len(result) > 0:
        s_date = result[0]['datetime'] + timedelta(days=1)
        if s_date.strftime("%A") == "Saturday":
            s_date = result[0]['datetime'] + timedelta(days=2)
        elif s_date.strftime("%A") == "Sunday":
            s_date = result[0]['datetime'] + timedelta(days=1)
    else:
        s_date = datetime.now() - timedelta(days=60)
        data_exists = False
    return s_date, datetime.now(), data_exists


def load_initial_data(instrument, s_date, e_date=datetime.now()):
    records = list(md.pmdb['HistoricalData'].find({'stock': instrument}))
    # try:
    if len(records) == 0:
        final_df = fetch_historical_stock_data(instrument, s_date, e_date)
        if final_df.shape[0] == 0:
            return

        md.pmdb['HistoricalData'].insert_many(final_df.to_dict('records'))
        print("Data inserted for " + instrument)
    else:
        print("Already data exist for " + instrument)
    # except Exception as ex:
    #     print(ex)


def get_mongo_data(record_count=100):
    result = list(md.pmdb['HistoricalData'].aggregate([
        {'$sort': {'datetime': 1}},
        {'$group': {
            "_id": "$stock",
            "stock": {'$last': '$stock'},
            'datetime': {'$last': '$datetime'},
            'delivery_list': {"$push": {"delivery": "$delivery"}},
        }
        },
        {
            '$project': {
                "datetime": "$datetime",
                "stock": "$stock",
                "delivery_list": {"$slice": ["$delivery_list", 5]},
            }
        },
        {
            '$project': {
                "datetime": "$datetime",
                "stock": "$stock",
                "avg_del": {"$avg": "$delivery_list.delivery"}
            }
        },
    ]))
    return list(result)


def prepare_daily_final_data(df, stock_data):
    df.loc[df.stock == stock_data['stock'], 'delivery_change'] = \
        df.loc[df.stock == stock_data['stock'], 'delivery'] * 100 / stock_data['avg_del']
    return df
    # for stock in stocks:


def prepare_left_historical_data(stock, s_date, e_date):
    db_data = list(md.pmdb['HistoricalData'].find({"stock": stock}).sort(
        [("datetime", 1)]).limit(90))
    db_df = pd.DataFrame(db_data)
    final_df = fetch_historical_stock_data(stock=stock, start_date=s_date, end_date=e_date)
    prev_row_count = db_df.shape[0]
    if final_df.shape[0] == 0:
        return

    db_df = db_df.append(final_df, ignore_index=True)
    db_df['price_change'] = db_df.close.pct_change() * 100
    db_df['avg_del'] = db_df['delivery'].rolling(5).mean()
    db_df['delivery_change'] = db_df['delivery'] * 100 / db_df['avg_del']
    db_df.round(2)
    db_df = db_df.loc[prev_row_count:, :]
    db_df.drop(columns=["_id"], inplace=True)
    md.pmdb['HistoricalData'].insert_many(db_df.to_dict('records'))
    print("Data inserted for " + stock)


# Daily Loading
def load_daily_bhav_copy():
    curr_datetime = datetime.now()
    if curr_datetime.hour >= 19:
        bhavcopy_date = date.today()
    else:
        bhavcopy_date = date.today() - timedelta(days=1)

    if bhavcopy_date.strftime("%A") == "Saturday":
        bhavcopy_date = bhavcopy_date - timedelta(days=1)
    elif bhavcopy_date.strftime("%A") == "Sunday":
        bhavcopy_date = bhavcopy_date - timedelta(days=2)
    try:
        bhavcopy = get_daily_eq_bhav_copy(bhavcopy_date)
    except:
        bhavcopy_date = bhavcopy_date - timedelta(days=1)
        bhavcopy = get_daily_eq_bhav_copy(bhavcopy_date)

    bhavcopy.rename(columns={'SYMBOL': 'stock', 'OPEN_PRICE': 'open', 'CLOSE_PRICE': 'close', 'LOW_PRICE': 'low',
                             'HIGH_PRICE': 'high', 'AVG_PRICE': 'vwap', 'DATE1': 'datetime'}, inplace=True)
    bhavcopy['delivery_change'] = np.nan
    return bhavcopy


# Steps for loading data
# 1. Check if data exists in database
# 2. If it does not exist call historical and load data from specified number of days in past
# 3. If it exist then check the last date and fill the data if some days are missing
# 4. If data is full then check for bhavcopy and update it in database

def equity_loader_main():
    for stock in stocks:
        print("Processing - " + stock)
        s_date, e_date, data_exists = get_dates_to_fetch(stock)
        try:
            if s_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                if not data_exists:
                    load_initial_data(stock, s_date, e_date)
                else:
                    prepare_left_historical_data(stock, s_date=s_date, e_date=e_date)
            else:
                print("Data upto date for stock - "+stock)
        except Exception as ex:
            print(ex)
            print("Error occured for " + stock)

    bhavcopy = load_daily_bhav_copy()
    bhavcopy['datetime'] = pd.to_datetime(bhavcopy['datetime'], format="%d-%b-%Y")
    bhavcopy = bhavcopy[bhavcopy.stock.isin(stocks)]
    bhavcopy.reset_index(inplace=True, drop=True)
    results = get_mongo_data()
    db_stock_list = []
    print("Processing bhavcopy")
    for result in results:
        db_stock_list.append(result['stock'])
        try:
            if result['datetime'] >= bhavcopy['datetime'][0]:
                bhavcopy = bhavcopy[bhavcopy.stock != result['stock']]
                bhavcopy.reset_index(inplace=True, drop=True)
            else:
                bhavcopy = prepare_daily_final_data(df=bhavcopy, stock_data=result)
            print("bhavcopy updated for "+result['stock'])
        except Exception as e:
            print(e)
            print("Error occured while processing bhavcopy for " + result['stock'])

    bhavcopy = bhavcopy[bhavcopy.stock.isin(db_stock_list)]
    bhavcopy.reset_index(inplace=True, drop=True)
    if bhavcopy.shape[0] > 0:
        md.pmdb['HistoricalData'].insert_many(bhavcopy.to_dict('records'))
        print("Data updated successfully")
    else:
        print("No new data available in bhavcopy")
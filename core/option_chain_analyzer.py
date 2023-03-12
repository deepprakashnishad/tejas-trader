from datetime import datetime
import numpy
import requests
import pandas as pd
import urllib.parse
from models.option_data import OptionData
import traceback
from models.index_option_data import IndexOptionData
from utils import my_constants as mconst
from termcolor import colored

url = "http://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
baseurl = "https://www.nseindia.com/"

class OptionChainAnalyzer:

    @classmethod
    def fetch_oi(cls, stock, type="equities"):
        # try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                     'like Gecko) '
                     'Chrome/80.0.3987.149 Safari/537.36',
       'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
        session = requests.Session()
        request = session.get(baseurl, headers=headers, timeout=5)
        cookies = dict(request.cookies)
        r = session.get("http://www.nseindia.com/api/option-chain-" + type + "?symbol="+urllib.parse.quote(stock),
                         timeout=15,
                         headers=headers , cookies=cookies).json()
        
        ce_values = [data['CE'] for data in r['records']['data'] if "CE" in data]
        pe_values = [data['PE'] for data in r['records']['data'] if "PE" in data]

        ce_data = pd.DataFrame(ce_values).groupby(['strikePrice']).sum()
        pe_data = pd.DataFrame(pe_values).groupby(['strikePrice']).sum()

        ce_data.drop(columns=["askPrice", "askQty", "bidQty", "bidprice", "totalBuyQuantity",
                              "totalSellQuantity", "totalTradedVolume", "underlyingValue",
                              "pchangeinOpenInterest", "impliedVolatility", "lastPrice",
                              "pChange"], axis=1, inplace=True)
        pe_data.drop(columns=["askPrice", "askQty", "bidQty", "bidprice", "totalBuyQuantity",
                              "totalSellQuantity", "totalTradedVolume", "underlyingValue",
                              "pchangeinOpenInterest", "impliedVolatility", "lastPrice",
                              "pChange"], axis=1, inplace=True)
        total_ce = ce_data.sum()
        total_pe = pe_data.sum()

        max_pain_ce = ce_data.nlargest(5, "openInterest")
        max_pain_pe = pe_data.nlargest(5, "openInterest")
        max_pain_ce.drop(columns=['changeinOpenInterest', 'change'], axis=1, inplace=True)
        max_pain_pe.drop(columns=['changeinOpenInterest', 'change'], axis=1, inplace=True)
        max_pain_ce.index = max_pain_ce.sort_index().index.astype(str, copy=False)
        max_pain_pe.index = max_pain_pe.sort_index().index.astype(str, copy=False)
        max_pain_ce = max_pain_ce.to_dict()
        max_pain_pe = max_pain_pe.to_dict()

        if total_ce['openInterest'] != 0:
            pcr = total_pe['openInterest'] / total_ce['openInterest']
        else:
            pcr = 999

        result = {
            "datetime": r['records']['timestamp'],
            "max_pain_ce": max_pain_ce['openInterest'],
            "max_pain_pe": max_pain_pe['openInterest'],
            "net_ce": total_ce['openInterest'],
            "net_pe": total_pe['openInterest'],
            "change_in_ce": total_ce['changeinOpenInterest'],
            "change_in_pe": total_pe['changeinOpenInterest'],
            "pcr": pcr,
        }
        OptionData.upsert({
            "datetime": datetime.strptime(r['records']['timestamp'], "%d-%b-%Y %H:%M:%S"),
            "stock": stock
        }, **{
            "datetime": datetime.strptime(r['records']['timestamp'], "%d-%b-%Y %H:%M:%S"),
            "max_pain_ce": max_pain_ce['openInterest'],
            "max_pain_pe": max_pain_pe['openInterest'],
            "net_ce": int(total_ce['openInterest']),
            "net_pe": int(total_pe['openInterest']),
            "pcr": float(pcr),
            "stock": stock
        })
        return result
        # except Exception as ex:
        #     print(colored(traceback.format_exc(), "red"))
        #     print(colored(f"Option data could not be saved for {stock}", "red"))
        #     return None

    @classmethod
    def fetch_option_chain(cls, stock, type="equities"):
        # try:
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                     'like Gecko) '
                     'Chrome/80.0.3987.149 Safari/537.36',
       'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
        session = requests.Session()
        request = session.get(baseurl, headers=headers, timeout=5)
        cookies = dict(request.cookies)
        mUrl = "http://www.nseindia.com/api/option-chain-" + type + "?symbol="+urllib.parse.quote(stock)
        r = session.get(mUrl,
                         timeout=15,
                         headers=headers , cookies=cookies).json()
        ce_values = [data['CE'] for data in r['records']['data'] if "CE" in data]
        pe_values = [data['PE'] for data in r['records']['data'] if "PE" in data]

        ce_data = pd.DataFrame(ce_values).groupby(['strikePrice']).sum()
        pe_data = pd.DataFrame(pe_values).groupby(['strikePrice']).sum()

        ce_data.drop(columns=["askPrice", "askQty", "bidQty", "bidprice", "totalBuyQuantity",
                              "totalSellQuantity", "totalTradedVolume", "underlyingValue",
                              "pchangeinOpenInterest", "impliedVolatility", "lastPrice",
                              "pChange"], axis=1, inplace=True)
        pe_data.drop(columns=["askPrice", "askQty", "bidQty", "bidprice", "totalBuyQuantity",
                              "totalSellQuantity", "totalTradedVolume", "underlyingValue",
                              "pchangeinOpenInterest", "impliedVolatility", "lastPrice",
                              "pChange"], axis=1, inplace=True)
        total_ce = ce_data.sum()
        total_pe = pe_data.sum()

        max_pain_ce = ce_data.nlargest(5, "openInterest")
        max_pain_pe = pe_data.nlargest(5, "openInterest")
        max_pain_ce.drop(columns=['changeinOpenInterest', 'change'], axis=1, inplace=True)
        max_pain_pe.drop(columns=['changeinOpenInterest', 'change'], axis=1, inplace=True)
        max_pain_ce.index = max_pain_ce.sort_index().index.astype(str, copy=False)
        max_pain_pe.index = max_pain_pe.sort_index().index.astype(str, copy=False)
        max_pain_ce = max_pain_ce.to_dict()
        max_pain_pe = max_pain_pe.to_dict()

        if total_ce['openInterest'] != 0:
            pcr = total_pe['openInterest'] / total_ce['openInterest']
        else:
            pcr = 999

        result = {
            "datetime": r['records']['timestamp'],
            "max_pain_ce": max_pain_ce['openInterest'],
            "max_pain_pe": max_pain_pe['openInterest'],
            "net_ce": total_ce['openInterest'],
            "net_pe": total_pe['openInterest'],
            "change_in_ce": total_ce['changeinOpenInterest'],
            "change_in_pe": total_pe['changeinOpenInterest'],
            "net_change": numpy.subtract(total_pe['changeinOpenInterest'], total_ce['changeinOpenInterest']),
            "stock": stock,
            "pcr": pcr,
        }
        return result

    def get_strikes(self, stock):
        response = self.fetch_oi()
        return response['records']['strikePrices']

    @classmethod
    def getIndexOI(cls):
        result = OptionChainAnalyzer.fetch_option_chain("NIFTY", "indices")
        mres = IndexOptionData.upsert({
            "datetime": result['datetime'],
            "stock": result['stock']
        }, **result)
        print(result)
        mconst.static_oi_data['nifty'].append(result)

        result = OptionChainAnalyzer.fetch_option_chain("BANKNIFTY", "indices")
        mres = IndexOptionData.upsert({
            "datetime": result['datetime'],
            "stock": result['stock']
        }, **result)
        mconst.static_oi_data['banknifty'].append(result)
        return

    @classmethod
    def cleanIndexOI(cls):
        mconst.static_oi_data = {"nifty":[], "banknifty":[]}
        IndexOptionData.deleteMany(**{})

def main(stock, type="equities"):
    OptionChainAnalyzer().fetch_oi(stock=stock, type=type)


if __name__ == '__main__':
    main("BANDHANBNK")
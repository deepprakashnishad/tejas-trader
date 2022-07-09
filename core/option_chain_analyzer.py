from datetime import datetime

import requests
import pandas as pd
import urllib.parse
import model as md
import traceback
from termcolor import colored

url = "http://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

class OptionChainAnalyzer:

    @classmethod
    def fetch_oi(cls, stock, type="equities"):
        try:
            r = requests.get("http://www.nseindia.com/api/option-chain-" + type + "?symbol="+urllib.parse.quote(stock),
                             timeout=15,
                             headers={'User-Agent': 'Mozilla/5.0'})

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

            md.pmdb["OptionData"].update({
                "datetime": r['records']['timestamp'],
                "stock": stock
            }, {"$set": {
                "datetime": datetime.strptime(r['records']['timestamp'], "%d-%b-%Y %H:%M:%S"),
                "max_pain_ce": max_pain_ce['openInterest'],
                "max_pain_pe": max_pain_pe['openInterest'],
                "net_ce": int(total_ce['openInterest']),
                "net_pe": int(total_pe['openInterest']),
                "pcr": float(pcr),
                "stock": stock
            }},
                True
            )
            return result
        except Exception as ex:
            print(colored(traceback.format_exc(), "red"))
            print(colored(f"Option data could not be saved for {stock}", "red"))
            return None

    def get_strikes(self, stock):
        response = self.fetch_oi()
        return response['records']['strikePrices']


def main(stock, type="equities"):
    OptionChainAnalyzer().fetch_oi(stock=stock, type=type)


if __name__ == '__main__':
    main("AUROPHARMA")
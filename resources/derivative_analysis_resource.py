import math

from flask_restful import Resource
from flask import Response, request, jsonify
from model import pmdb, MongoEngineJSONEncoder
from models.derivative_analysis_result import DerivativeAnalysisResult
from models.option_data import OptionData
from models.index_option_data import IndexOptionData
from models.historical_data import HistoricalData
import pandas as pd
from nse_derivative_loader import nse_derivative_loader_main
from nse_equity_db_loader import equity_loader_main
from core.option_chain_analyzer import OptionChainAnalyzer as oca
from utils import utilities
from utils import my_constants as mconst


class DerivativeAnalysisResource(Resource):

    def get(self):
        print("I visited here1")
        derivative_analysis_result = HistoricalData.aggregate([
            {
                '$project': {
                    "net_ce": {"$type": "$stock"}
                }
            }
        ]);
        # derivative_analysis_result = DerivativeAnalysisResult.aggregate([
        #     {'$sort': {
        #         'datetime': 1,
        #         'priority': -1
        #     }},
        #     {'$group': {
        #         "_id": "$stock",
        #         "stock": {'$last': '$stock'},
        #         'datetime': {'$last': '$datetime'},
        #         "open": {'$last': "$open"},
        #         "high": {'$last': "$high"},
        #         "low": {'$last': "$low"},
        #         "close": {'$last': "$close"},
        #         "coi_change": {'$last': "$coi_change"},
        #         "oi_combined": {'$last': "$oi_combined"},
        #         "delivery_change": {'$last': "$delivery_change"},
        #         "delivery": {'$last': "$delivery"},
        #         "vwap": {'$last': "$vwap"},
        #         "avg_del": {'$last': "$avg_del"},
        #         "price_change": {'$last': "$price_change"},
        #         "position": {'$last': "$position"},
        #         "priority": {'$last': "$priority"},
        #         "pcr": {'$last': "$pcr"},
        #         "pcr_of_change": {'$last': "$pcr_of_change"},
        #         "net_ce_change": {'$last': "$net_ce_change"},
        #         "net_pe_change": {'$last': "$net_pe_change"},
        #         "net_ce_change_pct": {'$last': "$net_ce_change_pct"},
        #         "net_pe_change_pct": {'$last': "$net_pe_change_pct"},
        #         "pivot_points": {'$last': "$pivot_points"},
        #     }},
        #     {
        #         '$project': {
        #             "datetime": "$datetime",
        #             "stock": "$stock",
        #             "open": "$open",
        #             "high": "$high",
        #             "low": "$low",
        #             "close": "$close",
        #             "type": {"$type": "$high"},
        #             "coi_change": {
        #                 '$switch': {
        #                     "branches": [
        #                         {
        #                             "case": {"$eq": [{"$type": "$coi_change"}, "string"]},
        #                             "then": "NaN"
        #                         }
        #                     ],
        #                     "default": "$coi_change"
        #                 }
        #             },
        #             "oi_combined": {
        #                 '$switch': {
        #                     "branches": [
        #                         {
        #                             "case": {"$eq": [{"$type": "$oi_combined"}, "string"]},
        #                             "then": "NaN"
        #                         }
        #                     ],
        #                     "default": "$oi_combined"
        #                 }
        #             },
        #             "delivery_change": "$delivery_change",
        #             "delivery": "$delivery",
        #             "vwap": "$vwap",
        #             "price_change": "$price_change",
        #             "position": "$position",
        #             "priority": "$priority",
        #             "pcr": "$pcr",
        #             "pcr_of_change": "$pcr_of_change",
        #             "net_ce_change": "$net_ce_change",
        #             "net_pe_change": "$net_pe_change",
        #             "net_ce_change_pct": "$net_ce_change_pct",
        #             "net_pe_change_pct": "$net_pe_change_pct",
        #             "pivot_points": "$pivot_points",
        #             "cpr_width": "$pivot_points.next.width"
        #         }
        #     }
        # ]);


        # derivative_analysis_result = list(pmdb['DerivativeAnalysisResult'].aggregate([
        #     {'$sort': {
        #         'datetime': 1,
        #         'priority': -1
        #     }},
        #     {'$group': {
        #         "_id": "$stock",
        #         "stock": {'$last': '$stock'},
        #         'datetime': {'$last': '$datetime'},
        #         "open": {'$last': "$open"},
        #         "high": {'$last': "$high"},
        #         "low": {'$last': "$low"},
        #         "close": {'$last': "$close"},
        #         "coi_change": {'$last': "$coi_change"},
        #         "oi_combined": {'$last': "$oi_combined"},
        #         "delivery_change": {'$last': "$delivery_change"},
        #         "delivery": {'$last': "$delivery"},
        #         "vwap": {'$last': "$vwap"},
        #         "avg_del": {'$last': "$avg_del"},
        #         "price_change": {'$last': "$price_change"},
        #         "position": {'$last': "$position"},
        #         "priority": {'$last': "$priority"},
        #         "pcr": {'$last': "$pcr"},
        #         "pcr_of_change": {'$last': "$pcr_of_change"},
        #         "net_ce_change": {'$last': "$net_ce_change"},
        #         "net_pe_change": {'$last': "$net_pe_change"},
        #         "net_ce_change_pct": {'$last': "$net_ce_change_pct"},
        #         "net_pe_change_pct": {'$last': "$net_pe_change_pct"},
        #         "pivot_points": {'$last': "$pivot_points"},
        #     }},
        #     {
        #         '$project': {
        #             "datetime": "$datetime",
        #             "stock": "$stock",
        #             "open": "$open",
        #             "high": "$high",
        #             "low": "$low",
        #             "close": "$close",
        #             "coi_change": "$coi_change",
        #             "oi_combined": "$oi_combined",
        #             "delivery_change": "$delivery_change",
        #             "delivery": "$delivery",
        #             "vwap": "$vwap",
        #             "price_change": "$price_change",
        #             "position": "$position",
        #             "priority": "$priority",
        #             "pcr": "$pcr",
        #             "pcr_of_change": "$pcr_of_change",
        #             "net_ce_change": "$net_ce_change",
        #             "net_pe_change": "$net_pe_change",
        #             "net_ce_change_pct": "$net_ce_change_pct",
        #             "net_pe_change_pct": "$net_pe_change_pct",
        #             "pivot_points": "$pivot_points",
        #             "cpr_width": "$pivot_points.next.width"
        #         }
        #     }
        # ]))
        return jsonify({"message": "Derivatives result", "result": derivative_analysis_result})


    def post(self):
        derivative_analysis_results = list(pmdb['DerivativeAnalysis']
                                          .find(
            {
                '$and': [
                    {'stock': "TATASTEEL"},
                    {'delivery_change': {'$ne': float('NaN')}}
                ]
            }
        ).sort([("stock", 1), ("datetime", 1)]))
        for i in range(0, len(derivative_analysis_results)-2):
            if derivative_analysis_results[i]['position'] == "Strong Long" \
                    and derivative_analysis_results[i+1]['price_change'] > 5\
                    and (derivative_analysis_results[i+1]['close'] - derivative_analysis_results[i+1]['open'])*100/\
                    derivative_analysis_results[i+1]['open'] > 3:
                derivative_analysis_results[i+1]['result'] = "Pass"
            elif derivative_analysis_results[i]['position'] in ["Long_Last_Leg", "Weaker Longs",
                                                                "Short Covering", "New Longs",
                                                                "Weak Long Covering", "No Short Position"]\
                   and derivative_analysis_results[i+1]['price_change'] > 5\
                    and (derivative_analysis_results[i+1]['close'] - derivative_analysis_results[i+1]['open'])*100/\
                    derivative_analysis_results[i+1]['open'] > 2:
                derivative_analysis_results[i+1]['result'] = "Pass"

            elif derivative_analysis_results[i]['position'] == "Strong Short" \
                    and derivative_analysis_results[i+1]['price_change'] < 5\
                    and (derivative_analysis_results[i+1]['close'] - derivative_analysis_results[i+1]['open'])*100/\
                    derivative_analysis_results[i+1]['open'] < -3:
                derivative_analysis_results[i+1]['result'] = "Pass"
            elif derivative_analysis_results[i]['position'] in ["Short_Last_Leg", "Weaker Shorts",
                                                                "Long Covering", "New Shorts",
                                                                "Weak Short Covering", "No Long Position"]\
                   and derivative_analysis_results[i+1]['price_change'] < 5\
                    and (derivative_analysis_results[i+1]['close'] - derivative_analysis_results[i+1]['open'])*100/\
                    derivative_analysis_results[i+1]['open'] < -2:
                derivative_analysis_results[i+1]['result'] = "Pass"
            elif derivative_analysis_results[i]['position'] == "No Interest"\
                   and 2 > derivative_analysis_results[i + 1]['price_change'] > -2 > (
                    derivative_analysis_results[i + 1]['close'] - derivative_analysis_results[i + 1]['open'])*100 / \
                    derivative_analysis_results[i + 1]['open']:
                derivative_analysis_results[i+1]['result'] = "Pass"
            else:
                derivative_analysis_results[i+1]['result'] = "Fail"

        df = pd.DataFrame(derivative_analysis_results)
        pass_count = df[df.result == "Pass"].shape[0]
        fail_count = df[df.result == "Fail"].shape[0]

        return jsonify({"message": "Derivatives result", "pass": pass_count, "fail": fail_count})
        # return jsonify({"message": "Derivatives result", "result": derivative_analysis_results})


class DetailedDerivativeAnalysisResource(Resource):

    def get(self, stock):
        derivative_analysis_result = list(pmdb['DerivativeAnalysisResult'].find(
            {'stock': stock},
            {"_id": 0, "avg_del": 1, "close": 1, "max_pain_ce": 1, "coi_change": 1, "datetime": 1,
             "delivery": 1, "delivery_change": 1, "high": 1, "low": 1, "max_pain_ce": 1, "max_pain_pe": 1,
             "net_ce_change": 1, "net_pe_change": 1, "net_ce_change_pct": 1, "net_pe_change_pct": 1, "oi_combined": 1, "open": 1, "pcr": 1, "pcr_of_change": 1,
             "position": 1, "price_change": 1, "priority": 1, "stock": 1, "vwap": 1, "pivot_points": 1, "net_pe": 1,
             "net_ce": 1}
        ).sort([("datetime", -1)]))
        temp = []
        for result in derivative_analysis_result:
            temp.append(utilities.dict_nan_cleaner(result))
        return jsonify({"message": "Derivatives result", "result": temp})

class DataLoaderAnalysisResource(Resource):
    def get(self, type):
        if type == "derivatives":
            nse_derivative_loader_main()
        else:
            equity_loader_main()
        return jsonify({"message": "Data processing completed"})        

class IndexOptionChainResource(Resource):

    # static_oi_data = {"nifty":[], "banknifty":[]}

    def get(self):
        oca.getIndexOI()
        return

    def put(self):
        IndexOptionChainResource.static_oi_data = {
            "nifty":[
                {
                    "_id": "64061fb425854a25967db274",
                    "change_in_ce": 218148,
                    "change_in_pe": 133319,
                    "datetime": "06-Mar-2023 09:30:00",
                    "max_pain_ce": {
                        "17700": 291892.5,
                        "17800": 218886.0,
                        "17900": 206218.0,
                        "18000": 168831.0,
                        "18100": 127000.0
                    },
                    "max_pain_pe": {
                        "17000": 288552.0,
                        "17400": 275398.0,
                        "17500": 192236.0,
                        "17600": 179841.0,
                        "17700": 178756.0
                    },
                    "net_change": 84828.5,
                    "net_ce": 2544195,
                    "net_pe": 2854470,
                    "pcr": 1.1219540954997553,
                    "stock": "NIFTY"
                },
                {
                    "_id": "64061fb425854a25967db274",
                    "change_in_ce": 210148,
                    "change_in_pe": 135319,
                    "datetime": "06-Mar-2023 09:32:00",
                    "max_pain_ce": {
                        "17700": 291892.5,
                        "17800": 218886.0,
                        "17900": 206218.0,
                        "18000": 168831.0,
                        "18100": 127000.0
                    },
                    "max_pain_pe": {
                        "17000": 288552.0,
                        "17400": 275398.0,
                        "17500": 192236.0,
                        "17600": 179841.0,
                        "17700": 178756.0
                    },
                    "net_change": 74829,
                    "net_ce": 2544195,
                    "net_pe": 2854470,
                    "pcr": 1.1219540954997553,
                    "stock": "NIFTY"
                },
                {
                    "_id": "64061fb425854a25967db274",
                    "change_in_ce": 208148,
                    "change_in_pe": 153319,
                    "datetime": "06-Mar-2023 09:34:00",
                    "max_pain_ce": {
                        "17700": 291892.5,
                        "17800": 218886.0,
                        "17900": 206218.0,
                        "18000": 168831.0,
                        "18100": 127000.0
                    },
                    "max_pain_pe": {
                        "17000": 288552.0,
                        "17400": 275398.0,
                        "17500": 192236.0,
                        "17600": 179841.0,
                        "17700": 178756.0
                    },
                    "net_change": 54829,
                    "net_ce": 2544195,
                    "net_pe": 2854470,
                    "pcr": 1.1219540954997553,
                    "stock": "NIFTY"
                },
                {
                    "_id": "64061fb425854a25967db274",
                    "change_in_ce": 219148,
                    "change_in_pe": 134319,
                    "datetime": "06-Mar-2023 09:36:00",
                    "max_pain_ce": {
                        "17700": 291892.5,
                        "17800": 218886.0,
                        "17900": 206218.0,
                        "18000": 168831.0,
                        "18100": 127000.0
                    },
                    "max_pain_pe": {
                        "17000": 288552.0,
                        "17400": 275398.0,
                        "17500": 192236.0,
                        "17600": 179841.0,
                        "17700": 178756.0
                    },
                    "net_change": 84829,
                    "net_ce": 2544195,
                    "net_pe": 2854470,
                    "pcr": 1.1219540954997553,
                    "stock": "NIFTY"
                },
            ], 
            "banknifty":[
                {
                    "_id": "6407422d25854a2596e4e17b",
                    "change_in_ce": 507748,
                    "change_in_pe": 93594,
                    "datetime": "06-Mar-2023 09:30:00",
                    "max_pain_ce": {
                        "41400": 191335,
                        "41500": 176023,
                        "42000": 150930,
                        "42500": 110387,
                        "43000": 109010
                    },
                    "max_pain_pe": {
                        "39000": 155591,
                        "40000": 142852,
                        "40500": 119382,
                        "41000": 101171,
                        "41300": 100651
                    },
                    "net_change": 414154,
                    "net_ce": 1995713,
                    "net_pe": 1993946,
                    "pcr": 0.9991146021497079,
                    "stock": "BANKNIFTY"
                },
                {
                    "_id": "6407422d25854a2596e4e17b",
                    "change_in_ce": 407748,
                    "change_in_pe": 193594,
                    "datetime": "06-Mar-2023 09:32:00",
                    "max_pain_ce": {
                        "41400": 191335,
                        "41500": 176023,
                        "42000": 150930,
                        "42500": 110387,
                        "43000": 109010
                    },
                    "max_pain_pe": {
                        "39000": 155591,
                        "40000": 142852,
                        "40500": 119382,
                        "41000": 101171,
                        "41300": 100651
                    },
                    "net_change": 215154,
                    "net_ce": 1995713,
                    "net_pe": 1993946,
                    "pcr": 0.9991146021497079,
                    "stock": "BANKNIFTY"
                },
                {
                    "_id": "6407422d25854a2596e4e17b",
                    "change_in_ce": 307748,
                    "change_in_pe": 293594,
                    "datetime": "06-Mar-2023 09:36:00",
                    "max_pain_ce": {
                        "41400": 191335,
                        "41500": 176023,
                        "42000": 150930,
                        "42500": 110387,
                        "43000": 109010
                    },
                    "max_pain_pe": {
                        "39000": 155591,
                        "40000": 142852,
                        "40500": 119382,
                        "41000": 101171,
                        "41300": 100651
                    },
                    "net_change": 14154,
                    "net_ce": 1995713,
                    "net_pe": 1993946,
                    "pcr": 0.9991146021497079,
                    "stock": "BANKNIFTY"
                },
                {
                    "_id": "6407422d25854a2596e4e17b",
                    "change_in_ce": 207748,
                    "change_in_pe": 393594,
                    "datetime": "06-Mar-2023 09:38:00",
                    "max_pain_ce": {
                        "41400": 191335,
                        "41500": 176023,
                        "42000": 150930,
                        "42500": 110387,
                        "43000": 109010
                    },
                    "max_pain_pe": {
                        "39000": 155591,
                        "40000": 142852,
                        "40500": 119382,
                        "41000": 101171,
                        "41300": 100651
                    },
                    "net_change": -203423,
                    "net_ce": 1995713,
                    "net_pe": 1993946,
                    "pcr": 0.9991146021497079,
                    "stock": "BANKNIFTY"
                },
                {
                    "_id": "6407422d25854a2596e4e17b",
                    "change_in_ce": 107748,
                    "change_in_pe": 493594,
                    "datetime": "06-Mar-2023 09:40:00",
                    "max_pain_ce": {
                        "41400": 191335,
                        "41500": 176023,
                        "42000": 150930,
                        "42500": 110387,
                        "43000": 109010
                    },
                    "max_pain_pe": {
                        "39000": 155591,
                        "40000": 142852,
                        "40500": 119382,
                        "41000": 101171,
                        "41300": 100651
                    },
                    "net_change": -243423,
                    "net_ce": 1995713,
                    "net_pe": 1993946,
                    "pcr": 0.9991146021497079,
                    "stock": "BANKNIFTY"
                },
            ]            
        }
        return jsonify(IndexOptionChainResource.static_oi_data)

    def post(self):
        if len(mconst.static_oi_data['nifty'])==0:
            result = IndexOptionData.list()
            for r in result:
                if r['stock']=="NIFTY":
                    mconst.static_oi_data['nifty'].append(r)
                else:                    
                    mconst.static_oi_data['banknifty'].append(r)
        return jsonify(mconst.static_oi_data)

    def delete(self, id):
        oca.cleanIndexOI()
        return
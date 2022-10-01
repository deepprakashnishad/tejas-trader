import math

from flask_restful import Resource
from flask import Response, request, jsonify
from model import pmdb, MongoEngineJSONEncoder
from models.derivative_analysis_result import DerivativeAnalysisResult
import pandas as pd
from nse_derivative_loader import nse_derivative_loader_main
from nse_equity_db_loader import equity_loader_main

from utils import utilities


class DerivativeAnalysisResource(Resource):

    def get(self):
        
        derivative_analysis_result = DerivativeAnalysisResult.aggregate([
            {'$sort': {
                'datetime': 1,
                'priority': -1
            }},
            {'$group': {
                "_id": "$stock",
                "stock": {'$last': '$stock'},
                'datetime': {'$last': '$datetime'},
                "open": {'$last': "$open"},
                "high": {'$last': "$high"},
                "low": {'$last': "$low"},
                "close": {'$last': "$close"},
                "coi_change": {'$last': "$coi_change"},
                "oi_combined": {'$last': "$oi_combined"},
                "delivery_change": {'$last': "$delivery_change"},
                "delivery": {'$last': "$delivery"},
                "vwap": {'$last': "$vwap"},
                "avg_del": {'$last': "$avg_del"},
                "price_change": {'$last': "$price_change"},
                "position": {'$last': "$position"},
                "priority": {'$last': "$priority"},
                "pcr": {'$last': "$pcr"},
                "pcr_of_change": {'$last': "$pcr_of_change"},
                "net_ce_change": {'$last': "$net_ce_change"},
                "net_pe_change": {'$last': "$net_pe_change"},
                "net_ce_change_pct": {'$last': "$net_ce_change_pct"},
                "net_pe_change_pct": {'$last': "$net_pe_change_pct"},
                "pivot_points": {'$last': "$pivot_points"},
            }},
            {
                '$project': {
                    "datetime": "$datetime",
                    "stock": "$stock",
                    "open": "$open",
                    "high": "$high",
                    "low": "$low",
                    "close": "$close",
                    "coi_change": "$coi_change",
                    "oi_combined": "$oi_combined",
                    "delivery_change": "$delivery_change",
                    "delivery": "$delivery",
                    "vwap": "$vwap",
                    "price_change": "$price_change",
                    "position": "$position",
                    "priority": "$priority",
                    "pcr": "$pcr",
                    "pcr_of_change": "$pcr_of_change",
                    "net_ce_change": "$net_ce_change",
                    "net_pe_change": "$net_pe_change",
                    "net_ce_change_pct": "$net_ce_change_pct",
                    "net_pe_change_pct": "$net_pe_change_pct",
                    "pivot_points": "$pivot_points",
                    "cpr_width": "$pivot_points.next.width"
                }
            }
        ]);
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
        derivative_analysis_result = list(pmdb['DerivativeAnalysis'].find(
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

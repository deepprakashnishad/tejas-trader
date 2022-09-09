from flask_restful import Resource
from flask import Response, request, jsonify

from brokers.test_broker import TestBroker
from core.tejas import Tejas
from core.tejas_run_modes import TejasRunModes
from strategies.strategy_builder import StrategyBuilder


class BacktestResource(Resource):

    def post(self):
        body = request.get_json()
        if 'user_id' not in body.keys():
            user_id = "DD1144"
        else:
            user_id = body['user_id']

        # feed = ZerodhaFeed(broker=None)
        tejas = Tejas(feed=feed, mode=TejasRunModes.BACKTEST, plot=True)
        # broker = ZerodhaBroker(uid=mconst.UID)
        broker = TestBroker()
        tejas.set_broker(broker)
        feed.set_broker(broker)
        strategy = body['strategy']
        tejas.add_strategy(StrategyBuilder(feed, strategy_name=strategy['name'],
                                           start_time=body['start'], end_time=body['end']))

        result = tejas.run()

        return jsonify({"msg": "This is a post request"})

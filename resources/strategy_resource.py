from flask_restful import Resource
from flask import Response, request, jsonify
from model import Strategy, Instrument, MongoEngineJSONEncoder


class StrategiesResource(Resource):
    def get(self):
        strategies = Strategy.query.all()
        return jsonify({"message": "Strategies fetched", "strategies": strategies})

    def post(self):
        body = request.get_json()
        return {"This is a put request"}

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        Strategy.remove()


class StrategyResource(Resource):
    def get(self, id):
        strategy = Strategy.query.get(id)
        return jsonify({"message": "Strategies fetched", "strategy": strategy})

    def post(self):
        body = request.get_json()
        strategy = Strategy()
        msg = f"{body['name']} created successfully"

        MongoEngineJSONEncoder.json_to_object(strategy, body)
        strategy.save()
        return jsonify({"msg": msg})

    def put(self, id):
        body = request.get_json()
        strategy = Strategy.query.get(id)
        MongoEngineJSONEncoder.json_to_object(strategy, body)
        strategy.save()
        return jsonify({"msg": f"{body['name']} updated successfully"})

    def delete(self, id):
        strategy = Strategy.query.get(id)
        result = strategy.remove()
        return jsonify({"msg": "Strategy deleted successfully", "result": result})

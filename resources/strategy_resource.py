from flask_restful import Resource
from flask import Response, request, jsonify
from models.strategy import Strategy


class StrategiesResource(Resource):
    def get(self):
        strategies = Strategy.list()
        return jsonify({"message": "Strategies fetched", "strategies": strategies})


class StrategyResource(Resource):
    def get(self, id):
        strategy = Strategy.get(**{"id":id})
        return jsonify({"message": "Strategies fetched", "strategy": strategy})

    def post(self):
        body = request.get_json()
        strategy = Strategy.create(**body)
        msg = f"{body['name']} created successfully"
        return jsonify({"msg": msg})

    def put(self):
        body = request.get_json()
        result = Strategy.update(body['_id'], **body)
        return jsonify({"msg": "Strategy updated successsfully", "result": result})

    def delete(self, _id):
        result = Strategy.delete(_id)
        return jsonify({"msg": "Strategy deleted successfully", "result": result})

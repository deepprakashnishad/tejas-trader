from flask_restful import Resource
from flask import Response, request, jsonify
from models.strategy import Strategy
from models.deploy_strategy import DeployStrategy
from resources.jwt_helper import decode

class StrategiesResource(Resource):
    def get(self):
        result = decode(request.headers)
        if result['status']=="success":
            filter = request.args.get("q")
            user_id = result['payload']['_id'];
            deployed_strategies = DeployStrategy.get(**{"_id": user_id})
            if filter is not None and filter=="my-strategies":
                user_id = result['payload']['_id'];
                strategies = Strategy.list(**{"ids": deployed_strategies['strategy_ids']})
            else:
                strategies = Strategy.list()
            
            return jsonify({"message": "Strategies fetched", "strategies": strategies, "deployed_strategies": deployed_strategies['strategy_ids']})
        else:
            strategies = Strategy.list()
            return jsonify({"message": "Strategies fetched", "strategies": strategies, "deployed_strategies": []})


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

from flask_restful import Resource
from flask import Response, request, jsonify
from models.deploy_strategy import DeployStrategy
from model import MongoEngineJSONEncoder

class DeployStrategyResource(Resource):
    def get(self, user_id):
        deployed_strategies = DeployStrategy.get(DeployStrategy.user_id == user_id)
        return jsonify({"message": "Deploys fetched", "strategies": deployed_strategies})

    def post(self):
        body = request.get_json()
        if 'user_id' not in body.keys():
            user_id = "DD1144"
        else:
            user_id = body['user_id']

        deployed_strategies_object = DeployStrategy.get(DeployStrategy.user_id == user_id)
        if not deployed_strategies_object:
            deployed_strategies_object = DeployStrategy(user_id=user_id, strategy_ids=body['strategy_ids'])
        else:
            deployed_strategies = MongoEngineJSONEncoder().default(deployed_strategies_object)
            temp_ids = list(set(body['strategy_ids']) - set(deployed_strategies['strategy_ids']))
            deployed_strategies['strategy_ids'].extend(temp_ids)
            MongoEngineJSONEncoder\
                .json_to_object(deployed_strategies_object, deployed_strategies)
        DeployedStrategy.create(**deployed_strategies_object)
        return jsonify({"msg": "This is a post request"})

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        DeployStrategy.remove(id)
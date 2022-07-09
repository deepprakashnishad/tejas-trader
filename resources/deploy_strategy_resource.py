from flask_restful import Resource
from flask import Response, request, jsonify
from model import DeployStrategy, MongoEngineJSONEncoder


# class DeploysResource(Resource):
#     def get(self):
#         Deploys = Deploy.query.all()
#         return jsonify(Deploys)
#
#     def post(self):
#         body = request.get_json()
#         Deploys = Deploy.getDeployBySymbols(body['ids'])
#
#         return jsonify(list(Deploys))
#
#     def put(self, id):
#         body = request.get_json()
#         return {"This is a put request"}
#
#     def delete(self, id):
#         Deploy.remove()


class DeployStrategyResource(Resource):
    def get(self, user_id):
        deployed_strategies = DeployStrategy.query.filter(DeployStrategy.user_id == user_id).first()
        return jsonify({"message": "Deploys fetched", "strategies": deployed_strategies})

    def post(self):
        body = request.get_json()
        if 'user_id' not in body.keys():
            user_id = "DD1144"
        else:
            user_id = body['user_id']

        deployed_strategies_object = DeployStrategy.query.filter(DeployStrategy.user_id == user_id).first()
        if not deployed_strategies_object:
            deployed_strategies_object = DeployStrategy(user_id=user_id, strategy_ids=body['strategy_ids'])
        else:
            deployed_strategies = MongoEngineJSONEncoder().default(deployed_strategies_object)
            temp_ids = list(set(body['strategy_ids']) - set(deployed_strategies['strategy_ids']))
            deployed_strategies['strategy_ids'].extend(temp_ids)
            MongoEngineJSONEncoder\
                .json_to_object(deployed_strategies_object, deployed_strategies)
        deployed_strategies_object.save()
        return jsonify({"msg": "This is a post request"})

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    # def delete(self, id):
    #     Deploy.remove()
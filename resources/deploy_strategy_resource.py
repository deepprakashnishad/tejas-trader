from flask_restful import Resource
from flask import Response, request, jsonify
from models.deploy_strategy import DeployStrategy
from model import MongoEngineJSONEncoder
from resources.jwt_helper import decode

class DeployStrategyResource(Resource):
    def get(self, user_id):
        result = decode(request.headers)
        if result['status']=="success":
            user_id = result['payload']['_id'];
            deployed_strategies = DeployStrategy.get(**{"_id": user_id})
            return jsonify({"message": "Deployed strategies fetched", "strategies": deployed_strategies})
        else:
            return jsonify(result)

    def post(self):
        body = request.get_json()
        try:
            result = decode(request.headers)
            if result['status']=="success":
                user_id = result['payload']['_id'];
                deployed_strategies = DeployStrategy.get(**{"_id": user_id})
                if deployed_strategies is not None:                    
                    deployed_strategies['strategy_ids'] = list(set(deployed_strategies['strategy_ids']) | set(body['strategy_ids']))
                else:
                    deployed_strategies = body
                DeployStrategy.upsert({"_id": user_id}, **deployed_strategies)
                
                return jsonify({"msg": "Strategy successfully deployed", "status": "success"})
            else:
                return jsonify(result)
        except Exception as e:
            print(e)
            return jsonify({"status": "error", "msg": "Error occured"})

    def put(self):
        body = request.get_json()
        try:
            result = decode(request.headers)
            if result['status']=="success":
                user_id = result['payload']['_id'];
                DeployStrategy.upsert({"_id": user_id}, **body)
                
                return jsonify({"msg": "Deployed strategy list updated successfully", "status": "success"})
            else:
                return jsonify(result)
        except Exception as e:
            print(e)
            return jsonify({"status": "error", "msg": "Error occured"})
        
    def delete(self, id):
        body = request.get_json()
        try:
            result = decode(request.headers)
            if result['status']=="success":
                user_id = result['payload']['_id'];
                deployed_strategies = DeployStrategy.get(**{"_id": user_id})
                if deployed_strategies is not None:                    
                    deployed_strategies['strategy_ids'] = list(set(deployed_strategies['strategy_ids']).difference(set(body['strategy_ids'])))
                    DeployStrategy.upsert({"_id": user_id}, **deployed_strategies)
                
                return jsonify({"msg": "Strategy removed successfully", "status": "success"})
            else:
                return jsonify(result)
        except Exception as e:
            print(e)
            return jsonify({"status": "error", "msg": "Error occured"})
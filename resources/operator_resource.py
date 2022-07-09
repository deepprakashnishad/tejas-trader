from flask_restful import Resource
from flask import Response, request, jsonify
from model import Operator, Instrument, MongoEngineJSONEncoder


class OperatorsResource(Resource):
    def get(self):
        operators = Operator.query.all()
        return jsonify(operators)

    def post(self):
        body = request.get_json()
        return {"This is a put request"}

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        Operator.remove()


class OperatorResource(Resource):
    def get(self, name):
        operator = Operator.query.filter(Operator.name == name).first()
        return jsonify({"message": "Operator fetched", "Operator": Operator})

    def post(self):
        body = request.get_json()
        operator = Operator()
        MongoEngineJSONEncoder.json_to_object(operator, body)
        operator.save()
        return jsonify({"msg": "Operator created successfully"})

    def put(self):
        body = request.get_json()
        operator = Operator.query.get(body['_id'])
        MongoEngineJSONEncoder.json_to_object(operator, body)
        operator.save()
        return jsonify({"msg": "Operator updated successsfully"})

    def delete(self, _id):
        operator = Operator.query.get(_id)
        result = operator.remove()
        return jsonify({"msg": "Operator deleted successfully"})

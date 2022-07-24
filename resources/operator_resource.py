from flask_restful import Resource
from flask import Response, request, jsonify
from models.operator import Operator


class OperatorsResource(Resource):
    def get(self):
        operators = Operator.list()
        return jsonify(operators)

    def delete(self, id):
        Operator.remove()


class OperatorResource(Resource):
    def get(self, name):
        operator = Operator.get(Operator.name == name).first()
        return jsonify({"message": "Operator fetched", "Operator": Operator})

    def post(self):
        body = request.get_json()
        operator = Operator.create(**body)
        return jsonify({"msg": "Operator created successfully"})

    def put(self):
        body = request.get_json()
        result = Operator.update(body['_id'], **body)
        return jsonify({"msg": "Operator updated successsfully", "result": result})

    def delete(self, _id):
        result = Operator.delete(_id)
        return jsonify({"msg": "Operator deleted successfully", "result": result})

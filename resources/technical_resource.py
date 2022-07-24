from flask_restful import Resource
from flask import Response, request, jsonify
from models.technical import Technical


class TechnicalsResource(Resource):
    def get(self):
        technicals = Technical.list()
        return jsonify(technicals)

    def delete(self, id):
        Technical.remove()


class TechnicalResource(Resource):
    def get(self, name):
        technical = Technical.get(Technical.name == name).first()
        return jsonify({"message": "Technical fetched", "technical": technical})

    def post(self):
        body = request.get_json()
        technical = Technical.create(**body)
        return jsonify({"msg": "Technical created successfully"})

    def put(self):
        body = request.get_json()
        result = Technical.update(body['_id'], **body)
        return jsonify({"msg": "Technical updated successsfully", "result": result})

    def delete(self, _id):
        result = Technical.delete(_id)
        return jsonify({"msg": "Technical deleted successfully", "result": result})

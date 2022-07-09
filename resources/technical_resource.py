from flask_restful import Resource
from flask import Response, request, jsonify
from model import Technical, Instrument, MongoEngineJSONEncoder


class TechnicalsResource(Resource):
    def get(self):
        technicals = Technical.query.all()
        return jsonify(technicals)

    def post(self):
        body = request.get_json()
        return {"This is a put request"}

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        Technical.remove()


class TechnicalResource(Resource):
    def get(self, name):
        technical = Technical.query.filter(Technical.name == name).first()
        return jsonify({"message": "Technical fetched", "technical": technical})

    def post(self):
        body = request.get_json()
        technical = Technical()
        MongoEngineJSONEncoder.json_to_object(technical, body)
        technical.save()
        return jsonify({"msg": "Technical created successfully"})

    def put(self):
        body = request.get_json()
        technical = Technical.query.get(body['_id'])
        MongoEngineJSONEncoder.json_to_object(technical, body)
        technical.save()
        return jsonify({"msg": "Technical updated successsfully"})

    def delete(self, _id):
        technical = Technical.query.get(_id)
        result = technical.remove()
        return jsonify({"msg": "Technical deleted successfully"})

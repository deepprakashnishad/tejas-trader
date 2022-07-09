from flask_restful import Resource
from flask import Response, request, jsonify
from model import Screener, Instrument, MongoEngineJSONEncoder


class ScreenersResource(Resource):
    def get(self):
        screeners = Screener.query.all()
        return jsonify({"message": "Screeners fetched", "screeners": screeners})

    def post(self):
        body = request.get_json()
        return {"This is a put request"}

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        Screener.remove()


class ScreenerResource(Resource):
    def get(self, id):
        screener = Screener.query.get(id)
        return jsonify({"message": "Screeners fetched", "screener": screener})

    def post(self):
        body = request.get_json()
        screener = Screener()
        msg = f"{body['name']} created successfully"

        MongoEngineJSONEncoder.json_to_object(screener, body)
        screener.save()
        return jsonify({"msg": msg})

    def put(self, id):
        body = request.get_json()
        screener = Screener.query.get(id)
        MongoEngineJSONEncoder.json_to_object(screener, body)
        screener.save()
        return jsonify({"msg": f"{body['name']} updated successfully"})

    def delete(self, id):
        screener = Screener.query.get(id)
        result = screener.remove()
        return jsonify({"msg": "Screener deleted successfully", "result": result})

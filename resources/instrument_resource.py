from flask_restful import Resource
from flask import Response, request, jsonify
from model import Instrument, Instrument, MongoEngineJSONEncoder


class InstrumentsResource(Resource):
    def get(self):
        instruments = Instrument.query.all()
        return jsonify(instruments)

    def post(self):
        body = request.get_json()
        instruments = Instrument.getInstrumentBySymbols(body['ids'])

        return jsonify(list(instruments))

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        Instrument.remove()


class InstrumentResource(Resource):
    def get(self, name):
        instrument = Instrument.query.filter(Instrument.name == name).first()
        return jsonify({"message": "Instruments fetched", "instrument": instrument})

    def post(self):
        body = request.get_json()
        instrument = Instrument()
        MongoEngineJSONEncoder.json_to_object(instrument, body)
        instrument.save()
        return jsonify({"msg": "This is a post request"})

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        Instrument.remove()
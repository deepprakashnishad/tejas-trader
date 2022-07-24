from flask_restful import Resource
from flask import Response, request, jsonify
from models.instrument import Instrument

class InstrumentsResource(Resource):
    def get(self):
        instruments = Instrument.list()
        return jsonify(instruments)

    def post(self):
        body = request.get_json()
        instruments = Instrument.getInstrumentBySymbols(body['ids'])
        return jsonify(list(instruments))

    def delete(self, id):
        Instrument.remove(id)


class InstrumentResource(Resource):
    def get(self, name):
        instrument = Instrument.get(Instrument.name == name).first()
        return jsonify({"message": "Instruments fetched", "instrument": instrument})

    def post(self):
        body = request.get_json()
        instrument = Instrument.create(**body)
        return jsonify({"msg": "Instrument created successfully", "instrument": instrument})

    def put(self, id):
        body = request.get_json()
        return {"This is a put request"}

    def delete(self, id):
        Instrument.remove(id)
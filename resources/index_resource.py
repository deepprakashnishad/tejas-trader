from flask_restful import Resource
from flask import Response, request, jsonify
from core.option_chain_analyzer import OptionChainAnalyzer as oca

class IndexOptionChainResource(Resource):
    def get(self):
        result = oca.fetch_option_chain("NIFTY", "index")
        return jsonify(result)

    def post(self):
        body = request.get_json()
        instruments = Instrument.getInstrumentBySymbols(body['ids'])
        return jsonify(list(instruments))

    def delete(self, id):
        Instrument.remove(id)
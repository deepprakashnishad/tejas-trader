from bson import ObjectId
from flask_restful import Resource
from flask import Response, request, jsonify
from model import pmdb, MongoEngineJSONEncoder
import datetime

from utils import utilities


class DailySelectionResource(Resource):

    def get(self):
        body = request.args
        results = list(pmdb['DailySelection'].find(
            # {"datetime": body['datetime']}
            {"datetime": datetime.datetime.strptime(body['datetime'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")}
        ))
        return jsonify({"message": "Records updates", "results": results})

    def put(self):
        data = request.get_json()
        result = pmdb['DailySelection'].update(
            {"stock": data['stock'], "datetime": data['datetime']},
            {"$set": data},
            True)
        if result['updatedExisting']:
            return jsonify({"message": "Records updates", "updatedExisting": result['updatedExisting']})
        else:
            return jsonify({"message": "Records updates",
                            "_id": str(result['upserted']), "updatedExisting": result['updatedExisting']})

    def delete(self, id):
        result = pmdb['DailySelection'].remove({"_id": ObjectId(id)})
        return jsonify({"message": "Record deleted", "deleted_record_count": result})
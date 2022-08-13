from flask_restful import Resource
from flask import Response, request, jsonify
from seed import seeddata
from utils.utilities import str_to_class

class SeedResource(Resource):
    def post(self):
        for mClass in seeddata:
            print(mClass)
            mCls=str_to_class(mClass["classname"])
            keys = mClass["keys"]
            for mData in mClass["data"]:
                conditions = {}
                for key in keys:
                    conditions[key] = mData[key]
                if len(conditions.keys())>0:
                    mCls.upsert(conditions, **mData)
        return jsonify({"message": "Seeding completed successfully", "status": "success"})
from flask.json import jsonify
from flask_restful import Resource
from flask import Response, request
from model import User, MongoEngineJSONEncoder, UserFundMargin


class UserResource(Resource):
    def get(self, uid):
        user = User.query.filter(User.user_id == uid).first()
        return jsonify({"message": "Algorithm executed", "users": user})
    
    def post(self):
        result = UserFundMargin(user_id="abc", equity=10000, commodity=15000).save()
        return {"I got your post request"}
    
    def algo_setup(self):
        return {"I got your algo setup request"}

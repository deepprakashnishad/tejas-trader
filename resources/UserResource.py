from flask.json import jsonify
from flask_restful import Resource
from flask import Response, request
from models.user import User


class UserResource(Resource):
    def get(self, uid):
        user = User.get(User.user_id == uid).first()
        return jsonify({"message": "Algorithm executed", "users": user})
    
    def post(self):
        data = request.get_json()
        condition = {}
        condition['user_id'] = data['user_id']
        condition['broker'] = data['broker']
        result = User.upsert(condition, **data)
        return jsonify(result)
    
    def algo_setup(self):
        return {"I got your algo setup request"}
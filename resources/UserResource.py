from flask.json import jsonify
from flask_restful import Resource
from flask import Response, request
from models.user import User


class UserResource(Resource):
    def get(self, uid):
        user = User.get(User.user_id == uid).first()
        return jsonify({"message": "Algorithm executed", "users": user})
    
    def post(self):
        result = UserFundMargin.create(user_id="abc", equity=10000, commodity=15000)
        # return {"I got your post request"}
    
    def algo_setup(self):
        return {"I got your algo setup request"}

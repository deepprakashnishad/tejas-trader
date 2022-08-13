from flask.json import jsonify
from flask_restful import Resource
from flask import Response, request,jsonify
from models.user import User
from authentication.login import Authenticate
import jwt
from resources.jwt_helper import encode



class AuthenticationResource(Resource):
    def get(self):
        authenticate=Authenticate()
        args = request.args
        args = args.to_dict()
        response = authenticate.get_access_token(args['request_token'])
        data = response['userdata']
        if data['avatar_url'] is None:
            del data['avatar_url']
        condition = {}
        condition['user_id'] = data['user_id']
        condition['broker'] = data['broker']
        result = User.upsert(condition, **data)

        token = encode({"_id":result["_id"], "user_id": data['user_id'], "broker": data['broker'], "user_name":data['user_name'], "email": data['email']})
        response['auth_token']=token
        # response = {'msg': 'Login successful.', 'status': True, 'userdata': {'user_type': 'individual', 'email': 'rishabh.r.garg@gmail.com', 'user_name': 'Rishabh Garg', 'user_shortname': 'Rishabh', 'broker': 'ZERODHA', 'exchanges': ['MCX', 'MF', 'BFO'], 'products': ['CNC', 'NRML', 'MIS', 'BO', 'CO'], 'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'], 'user_id': 'HN6243', 'api_key': '5za4lsjnw8rkesqm', 'access_token': 'MjxHMW8DQ39A2P5dgEgiFgNETldwXDyh', 'public_token': 'zKXZQGWLUMlj0QP3yVD1nXTAygCKHDJ8', 'refresh_token': '', 'enctoken': 'yjaH3aAuKyuQOuk7Oq7GnOC295AGChJAh0fxMDmIDUgSXNTisgUKaKPYKAYpfDsNubuWke+XDysCRnoN6M1x3Qu46adQzSiKBfIAR5mbVIBLuTTFxfdDHIxpB9fc+og=', 'meta': {'demat_consent': 'consent'}}, 'auth_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzb21lIjoicGF5bG9hZCJ9.lkoHj1c0zUyPd_oEOqtCSLoJKrjRh0qksFMkAdYPL7c'}
        return jsonify(response)
        
    
    def post(self):
        result = UserFundMargin.create(user_id="abc", equity=10000, commodity=15000)
        # return {"I got your post request"}
    
    def algo_setup(self):
        return {"I got your algo setup request"}
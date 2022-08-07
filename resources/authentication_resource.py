from flask.json import jsonify
from flask_restful import Resource
from flask import Response, request,jsonify
from models.user import User
from authentication.login import Authenticate
import jwt
from utils import my_constants as mconst


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

        encoded = jwt.encode({"some": "payload"}, mconst.SIGNING_KEY, algorithm=mconst.SIGNING_ALGO)
        response['auth_token']=encoded
        # response = {'msg': 'Login successful.', 'status': True, 'userdata': {'user_type': 'individual', 'email': 'rishabh.r.garg@gmail.com', 'user_name': 'Rishabh Garg', 'user_shortname': 'Rishabh', 'broker': 'ZERODHA', 'exchanges': ['MCX', 'MF', 'BFO'], 'products': ['CNC', 'NRML', 'MIS', 'BO', 'CO'], 'order_types': ['MARKET', 'LIMIT', 'SL', 'SL-M'], 'user_id': 'HN6243', 'api_key': '5za4lsjnw8rkesqm', 'access_token': 'MjxHMW8DQ39A2P5dgEgiFgNETldwXDyh', 'public_token': 'zKXZQGWLUMlj0QP3yVD1nXTAygCKHDJ8', 'refresh_token': '', 'enctoken': 'yjaH3aAuKyuQOuk7Oq7GnOC295AGChJAh0fxMDmIDUgSXNTisgUKaKPYKAYpfDsNubuWke+XDysCRnoN6M1x3Qu46adQzSiKBfIAR5mbVIBLuTTFxfdDHIxpB9fc+og=', 'meta': {'demat_consent': 'consent'}}, 'auth_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzb21lIjoicGF5bG9hZCJ9.lkoHj1c0zUyPd_oEOqtCSLoJKrjRh0qksFMkAdYPL7c'}
        return jsonify(response)
        
    
    def post(self):
        result = UserFundMargin.create(user_id="abc", equity=10000, commodity=15000)
        # return {"I got your post request"}
    
    def algo_setup(self):
        return {"I got your algo setup request"}
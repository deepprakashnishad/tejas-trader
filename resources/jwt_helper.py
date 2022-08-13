import jwt
from utils import my_constants as mconst

def encode(payload):
	return jwt.encode(payload, mconst.SIGNING_KEY, algorithm=mconst.SIGNING_ALGO)

def decode(headers):
	try:
		if "Authorization" not in headers:
			return {"status": "error", "msg": "Authorization token missing"}
		else:
			auth_header = headers["Authorization"]
			auth_headers = auth_header.split(" ")
			if auth_headers[1] is None:
				return {"status": "error", "msg": "Token missing in Authorization header"}
			else:
				token = auth_headers[1]
				payload = jwt.decode(token, mconst.SIGNING_KEY, algorithms=mconst.SIGNING_ALGO)

				return {"payload": payload, "status": "success"}
	except jwt.exceptions.InvalidTokenError:
		return {"status": "error", "msg": "Invalid authorization token"}
	except jwt.exceptions.DecodeError:
		return {"status": "error", "msg": "Token cannot be decoded because validation failed"}
	except jwt.exceptions.InvalidSignatureError:
		return {"status": "error", "msg": "Token signature is invalid"}
	except jwt.exceptions.ExpiredSignatureError:
		return {"status": "error", "msg": "Token expired"}
	except jwt.exceptions.InvalidAudienceError:
		return {"status": "error", "msg": "Invalid audience contained in token"}
	except jwt.exceptions.InvalidIssuerError:
		return {"status": "error", "msg": "Invalid issuer"}
	except jwt.exceptions.InvalidIssuedAtError:
		return {"status": "error", "msg": "Token used prior to it's start time"}
	except jwt.exceptions.InvalidKeyError:
		return {"status": "error", "msg": "InvalidKeyError"}
	except jwt.exceptions.InvalidAlgorithmError:
		return {"status": "error", "msg": "InvalidAlgorithmError"}
	except jwt.exceptions.MissingRequiredClaimError:
		return {"status": "error", "msg": "MissingRequiredClaimError"}
	except jwt.exceptions.ImmatureSignatureError:
		return {"status": "error", "msg": "ImmatureSignatureError"}
	except:
		return {"status": "error", "msg": "Some error occurred while decoding the token"}
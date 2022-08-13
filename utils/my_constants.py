ENV = "PROD"

STRATEGY_EXEC_INTERVAL_IN_MILLISEC=60000

SIGNING_KEY="ab87ed58b2msh78f8c53185c415bp161123jsnff19e78ce6eb"
SIGNING_ALGO = "HS256"

API_KEY = "5za4lsjnw8rkesqm"
API_SECRET = "73lr878npf01p45yzesfszyndsjwsu3j"
AUTH_URL = f"https://kite.trade/connect/login?v=3&api_key={API_KEY}"
ACCESS_TOKEN = ""
UID = "HN6243"
MAXINT = 99999999
ALPHA_KEY = "8O8PGS7VDPEHNS5A"
ALPHA_URL = "https://www.alphavantage.co/"

DB_NAME = "quantTrader"
DB_URL = f"mongodb://localhost:27017/{DB_NAME}"
DEV_REPLICA_SET = "rs0"
# DB_SERVER_URL = "mongodb://localhost:27017/"

PROD_DB_NAME = "quantTrader"
PROD_REPLICA_SET = "atlas-l9f6r8-shard-0"
PROD_DB_URL = "mongodb://stockedge:SnGAcQYwC9jUWGXY@cluster0-shard-00-00.gexxa.mongodb.net:27017,cluster0-shard-00-01.gexxa.mongodb.net:27017,cluster0-shard-00-02.gexxa.mongodb.net:27017/quantTrader?ssl=true&replicaSet=atlas-l9f6r8-shard-0&authSource=admin&retryWrites=false&w=majority"
# PROD_DB_URL = "mongodb+srv://stockedge:SnGAcQYwC9jUWGXY@cluster0.gexxa.mongodb.net/quantTrader?retryWrites=true&w=majority&replicaSet=atlas-l9f6r8-shard-0"


RAPID_API_KEY = "ab87ed58b2msh78f8c53185c415bp161652jsnff19e78ce6eb"
RAPID_API_URL = "https://morningstar1.p.rapidapi.com"


DELIVERY_MULTIPLIER = 1
COI_MULTIPLIER = 1
PRICE_MULTIPLIER = 0.7

PCR_WEIGHT = 2
PE_CE_DIFF_WEIGHT = 0.2
COI_WEIGHT = 2
DELIVERY_WEIGHT = 0.02

DAYS_FOR_AVG_DELIVERY = 5
DAYS_FOR_CHANGE_MEAN = 20
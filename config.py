import os
from utils import my_constants as mconst

# You need to replace the next values with the appropriate values for your configuration

basedir = os.path.abspath(os.path.dirname(__file__))

env = mconst.ENV;

if env=="PROD":
    db_url = mconst.PROD_DB_URL
    db_name = mconst.PROD_DB_NAME
    MONGOALCHEMY_REPLICA_SET = mconst.PROD_REPLICA_SET
    DEBUG = False
else:
    db_url = mconst.DB_URL
    db_name = mconst.DB_NAME
    MONGOALCHEMY_REPLICA_SET = mconst.DEV_REPLICA_SET
    DEBUG = True

MONGOALCHEMY_DATABASE=db_name
MONGOALCHEMY_CONNECTION_STRING=db_url
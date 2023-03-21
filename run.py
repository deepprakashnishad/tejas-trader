from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from mongoengine_jsonencoder import MongoEngineJSONEncoder
from utils import my_constants as mconst
from utils.utilities import is_access_token_valid, is_time_between
from core.option_chain_analyzer import OptionChainAnalyzer as oca
import datetime as dt

app = Flask(__name__)
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config.from_object("config")

from app import api_bp

app.register_blueprint(api_bp, url_prefix='/api')

from model import db, MongoEngineJSONEncoder
# from run_tejas import start_tejas
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time 
app.json_encoder = MongoEngineJSONEncoder
db.init_app(app)
global stop_threads

def fetch_live_index_oi():
    print("Fetching IndexOI Data")
    if is_time_between(dt.time(9, 15), dt.time(15,30)):
        oca.getIndexOI()
    else:
        if  dt.datetime.now().time() > dt.time(15,30):
            print("Market Closed")

def clean_live_index_oi():
    print("Cleaning in progress")
    oca.cleanIndexOI()

# def scheduleLiveIndexFetch():
print("Scheduling Jobs")
sched = BackgroundScheduler(daemon=True)
sched.add_job(fetch_live_index_oi,'cron', day_of_week='mon-fri', hour='*', minute='*', timezone='Asia/Kolkata')
sched.add_job(clean_live_index_oi,'cron', day_of_week='mon-fri', hour=9, minute='01-10', timezone='Asia/Kolkata')
sched.start()

# tejas_thread = threading.Thread(target=start_tejas, name='tejas')

@app.route('/')
def hello_world():
    return 'Welcome to Kite Autotrader'

# @app.route('/start_tejas')
# def start_tejas():
#     stop_threads=True
#     time.sleep(4)
#     stop_threads=False
#     isAlive = tejas_thread.is_alive()
#     if not isAlive:
#         tejas_thread.start()
#         return 'Tejas Started'
#     else:
#         return 'Tejas already running'

# @app.route('/stop_tejas')
# def stop_tejas():
#     stop_threads=True
#     return 'Tejas Stopped'

@app.route('/temp')
def temp():
    result = is_access_token_valid("2022-08-15T21:11:09.000+00:00")
    return result


# def create_app(config_filename):
#     app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
#     app.config.from_object(config_filename)

#     from app import api_bp
    
#     app.register_blueprint(api_bp, url_prefix='/api')

#     from model import db, MongoEngineJSONEncoder
#     app.json_encoder = MongoEngineJSONEncoder
#     db.init_app(myapp)

#     return app

if __name__ == "__main__":
    if mconst.ENV=="PROD":
        app.run()
    else:
        app.run(debug=True, port=5002)
from flask import Flask, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from mongoengine_jsonencoder import MongoEngineJSONEncoder
from utils import my_constants as mconst
from utils.utilities import is_access_token_valid

app = Flask(__name__)
CORS(app)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config.from_object("config")

from app import api_bp

app.register_blueprint(api_bp, url_prefix='/api')

from model import db, MongoEngineJSONEncoder
from run_tejas import start_tejas
import threading
import time

app.json_encoder = MongoEngineJSONEncoder
db.init_app(app)
global stop_threads

tejas_thread = threading.Thread(target=start_tejas, name='tejas')

@app.route('/')
def hello_world():
    return 'Welcome to Kite Autotrader'

@app.route('/start_tejas')
def start_tejas():
    stop_threads=True
    time.sleep(4)
    stop_threads=False
    isAlive = tejas_thread.is_alive()
    if not isAlive:
        tejas_thread.start()
        return 'Tejas Started'
    else:
        return 'Tejas already running'

@app.route('/stop_tejas')
def stop_tejas():
    stop_threads=True
    return 'Tejas Stopped'

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
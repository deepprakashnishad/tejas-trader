from flask import Flask
from flask_pymongo import PyMongo
from mongoengine_jsonencoder import MongoEngineJSONEncoder
from utils import my_constants as mconst

myapp = Flask(__name__)

def create_app(config_filename):
    myapp.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    myapp.config.from_object(config_filename)

    from app import api_bp
    
    myapp.register_blueprint(api_bp, url_prefix='/api')

    from model import db, MongoEngineJSONEncoder
    myapp.json_encoder = MongoEngineJSONEncoder
    db.init_app(myapp)

    return myapp

if __name__ == "__main__":
    app = create_app("config")
    if mconst.ENV=="PROD"
        app.run()
    else
        app.run(debug=True, port=5002)
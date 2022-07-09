from flask import Flask
from flask_pymongo import PyMongo
from mongoengine_jsonencoder import MongoEngineJSONEncoder
from utils import my_constants as mconst

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config.from_object("config")

from app import api_bp

app.register_blueprint(api_bp, url_prefix='/api')

from model import db, MongoEngineJSONEncoder
app.json_encoder = MongoEngineJSONEncoder
db.init_app(app)

@app.route('/')
def hello_world():
    return 'Welcome to Kite Autotrader'

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
    app = create_app("config")
    if mconst.ENV=="PROD":
        app.run()
    else:
        app.run(debug=True, port=5002)
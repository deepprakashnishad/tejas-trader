from flask import Flask
from flask_mongoalchemy import MongoAlchemy

app = Flask(__name__)

db = MongoAlchemy(app)


class Example(db.Document):
    name = db.StringField()

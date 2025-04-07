"""
Web app initialization
"""
import os
from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from .routes import main
from .auth import auth

mongo = PyMongo()


def create_app():
    """
    initialize app
    """
    load_dotenv()

    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.secret_key = os.getenv("SECRET_KEY")

    mongo.init_app(app)
    db = mongo.db  # pylint: disable=invalid-name

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app, db

from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
import os


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.secret_key = os.getenv("SECRET_KEY")

    # Set up pymongo client and attach to app
    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.db = mongo_client.get_default_database()  # auto-selects the db from the URI

    # Register blueprints
    from .routes import main
    from .auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app

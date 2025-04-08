"""
Initialize app
"""

import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient


def create_app():
    """
    Set up app
    """
    load_dotenv()

    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.secret_key = os.getenv("SECRET_KEY")

    # Set up pymongo client and attach to app
    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.db = mongo_client.get_default_database()  # auto-selects the db from the URI

    # Register blueprints
    from .routes import main # pylint: disable=import-outside-toplevel
    from .auth import auth # pylint: disable=import-outside-toplevel

    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app

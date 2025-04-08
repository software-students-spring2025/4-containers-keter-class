import os
import tempfile
import pytest
from app import create_app
from pymongo import MongoClient
import werkzeug

werkzeug.__version__ = "2.3.7"  # Monkey patch to prevent AttributeError


@pytest.fixture
def app():
    # Use a temp test DB
    os.environ["MONGO_URI"] = "mongodb://localhost:27017/test_flaskdb"
    os.environ["SECRET_KEY"] = "testing"

    app = create_app()

    # Drop users collection before each test for a clean slate
    with app.app_context():
        app.db.users.delete_many({})

    return app


@pytest.fixture
def client(app):
    return app.test_client()

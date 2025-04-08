"""
idk
"""

import os
import pytest
import werkzeug
from app import create_app

werkzeug.__version__ = "2.3.7"  # Monkey patch to prevent AttributeError


@pytest.fixture
def app():
    """
    idk
    """
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
    """
    idk
    """
    return app.test_client()

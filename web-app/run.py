"""
Start up app
"""

from app import create_app
from flask_cors import CORS

app = create_app()

# Allow CORS from localhost:5001
CORS(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)

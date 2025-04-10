"""
Testing the card parser with real card images
"""
import os
import json
import pytest
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

from main import app, parse_card_info, detect_text, client

# Define expected results for each test image
EXPECTED_RESULTS = {
    "card1.png": {
        "text": "1234 5678 9012 3456 Valid Thru: 01/26 JOHN DOE",
        "parsed": {
            "cardholder_name": "CARDHOLDER NAME",
            "card_number": "4019 1234 5678 9010",
            "cvv": "000",
            "expiry_date": "00/00"
        }
    }
}

@pytest.fixture
def client_app():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def read_image(filename):
    """Helper function to read image data from file."""
    images_dir = Path(__file__).parent.parent / "images"
    with open(images_dir / filename, "rb") as f:
        return f.read()

class TestCardScanner:
    @pytest.mark.parametrize("image_file", ["card1.png"])
    def test_text_detection_with_real_images(self, image_file, mocker):
        """
        Test text detection using real card images but mock the Vision API response.
        This allows us to test our parsing logic with known inputs.
        """
        image_data = read_image(image_file)

        mock_text = MagicMock()
        mock_text.description = EXPECTED_RESULTS[image_file]["text"]

        mock_response = MagicMock()
        mock_response.text_annotations = [mock_text]
        mock_response.error.message = ""

        mocker.patch.object(client, 'text_detection', return_value=mock_response)

        result = detect_text(image_data)

        assert result == EXPECTED_RESULTS[image_file]["text"]

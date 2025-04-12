"""
Testing the card parser with real card images
"""

import json
from io import BytesIO
from unittest.mock import MagicMock
import pytest

from main import app, parse_card_info, detect_text, api_client

EXPECTED_RESULTS = {
    "card1.png": {
        "text": "4019 1234 5678 9010 Valid Thru: 00/00 CARDHOLDER NAME",
        "parsed": {
            "cardholder_name": "CARDHOLDER NAME",
            "card_number": "4019 1234 5678 9010",
            "cvv": None,
            "expiry_date": "00/00",
            "errors": ['cvv']
        },
    },
    "card2.png": {
        "text": "2221 0012 3412 3456 Valid Thru: 12/23 Lee M. Cardholder",
        "parsed": {
            "cardholder_name": "Lee M. Cardholder",
            "card_number": "2221 0012 3412 3456",
            "cvv": None,
            "expiry_date": "12/23",
            "errors": ['cvv']
        },
    },
    "card3.png": {
        "text": "1234 4321 1010 5454 Valid Thru: 01/26 123 JOHN JACOB JINGLEHEIMER SCHMIDT",
        "parsed": {
            "cardholder_name": "JOHN JACOB JINGLEHEIMER SCHMIDT",
            "card_number": "1234 4321 1010 5454",
            "cvv": "123",
            "expiry_date": "01/26",
            "errors": []
        },
    },
    "card4.png": {
        "text": "",
        "parsed": {
            "cardholder_name": None,
            "card_number": None,
            "cvv": None,
            "expiry_date": None,
            "errors": ['cardholder name', 'card number', 'cvv', 'expiry date']
        },
    },
}


@pytest.fixture
def test_client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as flask_client:
        yield flask_client


def read_image(filename):  # pylint: disable=unused-argument
    """Helper function that returns mock data instead of reading files."""
    return b"mock_image_data"


class TestCardScanner:
    """
    Tests for the Google OCR API and credit card info parser
    """

    @pytest.mark.parametrize("image_file", ["card1.png", "card2.png", "card3.png", "card4.png"])
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

        mocker.patch.object(api_client, "text_detection", return_value=mock_response)

        result = detect_text(image_data)

        assert result == EXPECTED_RESULTS[image_file]["text"]

    @pytest.mark.parametrize("image_file", ["card1.png", "card2.png", "card3.png", "card4.png"])
    # pylint: disable=too-many-locals
    def test_parse_card_info_with_real_images(self, image_file, mocker):
        """
        Test the complete flow from text detection to parsing with real images.
        """

        image_data = read_image(image_file)

        mock_text = MagicMock()
        mock_text.description = EXPECTED_RESULTS[image_file]["text"]

        mock_response = MagicMock()
        mock_response.text_annotations = [mock_text]
        mock_response.error.message = ""

        mocker.patch.object(api_client, "text_detection", return_value=mock_response)

        detected_text = detect_text(image_data)

        username = "test_user"
        cardname = f"test_{image_file}"
        (
            cardholder_name,
            card_number,
            cvv,
            expiry_date,
            ret_username,
            ret_cardname,
            errors
        ) = parse_card_info(detected_text, username, cardname)

        expected = EXPECTED_RESULTS[image_file]["parsed"]
        assert cardholder_name == expected["cardholder_name"]
        assert card_number == expected["card_number"]
        assert cvv == expected["cvv"]
        assert expiry_date == expected["expiry_date"]
        assert ret_username == username
        assert ret_cardname == cardname
        assert errors == expected['errors']

    @pytest.mark.parametrize("image_file", ["card1.png", "card2.png", "card3.png"])
    # pylint: disable=redefined-outer-name
    def test_api_endpoint_with_real_images(self, image_file, test_client, mocker):
        """
        Test the complete API endpoint using real images.
        """
        # Load the real image data
        image_data = read_image(image_file)

        # Mock the text detection to return our predefined text
        mock_text = MagicMock()
        mock_text.description = EXPECTED_RESULTS[image_file]["text"]

        mock_response = MagicMock()
        mock_response.text_annotations = [mock_text]
        mock_response.error.message = ""

        mocker.patch.object(api_client, "text_detection", return_value=mock_response)

        data = {
            "file": (BytesIO(image_data), image_file),
            "username": "test_user",
            "cardname": f"test_{image_file}",
        }

        response = test_client.post(
            "/api/scan", data=data, content_type="multipart/form-data"
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data["success"] is True

        expected = EXPECTED_RESULTS[image_file]["parsed"]
        card_info = response_data["card_info"]
        assert card_info["cardholder_name"] == expected["cardholder_name"]
        assert card_info["card_number"] == expected["card_number"]
        assert card_info["cvv"] == expected["cvv"]
        assert card_info["expiry_date"] == expected["expiry_date"]
        assert card_info["username"] == "test_user"
        assert card_info["cardname"] == f"test_{image_file}"

# pylint: disable=redefined-outer-name
def test_scan_card_internal_server_error(test_client, mocker):
    """
    Test that the scan_card route handles exceptions correctly and returns a 500 error.
    """

    file_content = b"mock_image_data"
    data = {
        "file": (BytesIO(file_content), "test_card.png"),
        "username": "test_user",
        "cardname": "test_card",
    }

    def mock_detect_text(content):
        if content == file_content:
            raise RuntimeError("Simulated error")
        return ""

    mocker.patch("main.detect_text", side_effect=mock_detect_text)

    response = test_client.post(
        "/api/scan", 
        data=data, 
        content_type="multipart/form-data"
    )

    assert response.status_code == 500

    response_data = json.loads(response.data)

    assert "error" in response_data
    assert "Internal Server Error" in response_data["error"]
    assert "Simulated error" in response_data["error"]

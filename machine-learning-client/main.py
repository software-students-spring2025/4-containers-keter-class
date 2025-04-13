# pylint: disable=no-name-in-module,reimported,import-error
"""
Machine learning API and parsing and storage of credit card information
"""

import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import vision

app = Flask(__name__)
CORS(app)

if os.environ.get("PYTEST_CURRENT_TEST") is None:
    from google.cloud import vision

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secrets.json"
    api_client = vision.ImageAnnotatorClient()
else:
    from unittest.mock import MagicMock
    from google.cloud import vision

    api_client = MagicMock()


def detect_text(content):
    """Detects text in an image file (raw bytes)."""
    image = vision.Image(content=content)

    response = api_client.text_detection(image=image)  # pylint: disable=no-member
    texts = response.text_annotations

    if response.error.message:
        raise RuntimeError(
            f"{response.error.message}\nSee: https://cloud.google.com/apis/design/errors"
        )

    if not texts:
        return ""

    print("🔍 OCR Result:\n", texts[0].description)
    return texts[0].description


def parse_card_info(card_scan, username, cardname):
    """
    Extracts cardholder name, number, CVV, and expiry date from scanned text.
    """

    errors = []

    cardholder_name = "CARDHOLDER NAME"
    cardholder_names = re.findall(
        r"\b[A-Za-z]+(?:\s+[A-Za-z]\.?)?(?:\s+[A-Za-z]+)+\b", card_scan, re.IGNORECASE
    )

    filtered_names = [
        name
        for name in cardholder_names
        if not any(
            x.upper() in name.upper()
            for x in [
                "\n",
                "BUSINESS",
                "WORLD",
                "THRU",
                "GOOD THRU",
                "VALID THRU",
                "GOOD",
                "VISA",
                "CREDIT",
                "UNION",
                "TEXAS",
                "REWARDS",
                "AMERICAN",
                "EXPRESS",
                "MASTER",
                "GOLD",
                "BLACK",
                "DISCOVER",
                "BILT",
                "SEC CODE",
                "VALID",
            ]
        )
    ]

    if filtered_names:
        cardholder_name = filtered_names[0]

    if len(filtered_names) != 1:
        errors.append("cardholder name")
        cardholder_name = filtered_names or None

    card_number = re.findall(r"\d{4} \d{4} \d{4} \d{4}", card_scan)
    if len(card_number) != 1:
        errors.append("card number")
        card_number = None
    else:
        card_number = card_number[0]

    cvv = re.findall(r"(?<![.-])\b\d{3}\b(?![.-]\d)", card_scan)
    cvv = cvv[0] if cvv else None
    if not cvv:
        errors.append("cvv")

    expiry_date = re.findall(r"\d{2}\/\d{2}", card_scan)
    expiry_date = expiry_date[-1] if expiry_date else None
    if not expiry_date:
        errors.append("expiry date")

    return cardholder_name, card_number, cvv, expiry_date, username, cardname, errors


@app.route("/api/scan", methods=["POST"])
def scan_card():
    """
    Access CV to get text information from image
    Parse card information from text information
    Return information to web app
    """
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        username = request.form.get("username", "default_user")
        cardname = request.form.get("cardname", "unnamed_card")

        image_content = file.read()
        text = detect_text(image_content)  # ← could be the error!

        if not text:
            return jsonify({"error": "No text detected in image"}), 400

        card_info = parse_card_info(text, username, cardname)

        card_data = {
            "cardholder_name": card_info[0],
            "card_number": card_info[1],
            "cvv": card_info[2],
            "expiry_date": card_info[3],
            "username": username,
            "cardname": cardname,
        }

        urlthing = "retrieve"
        query_string = "&".join([f"{key}={value}" for key, value in card_data.items()])
        redirect_url = f"http://localhost:5002/{urlthing}?{query_string}"

        if os.environ.get("PYTEST_CURRENT_TEST") is not None:
            return jsonify({"success": True, "card_info": card_data}), 200

        # Redirect to the verify_info page with the card data
        return jsonify(
            {"success": True, "redirect_url": redirect_url, "card_data": card_data}
        )

    except Exception as e:  # pylint: disable=broad-exception-caught
        import traceback  # pylint: disable=import-outside-toplevel

        traceback.print_exc()
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)

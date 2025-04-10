"""
Machine learning API and parsing and storage of credit card information
"""

import os
import re
import requests
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from google.cloud import vision  # pylint: disable=no-name-in-module

app = Flask(__name__)
CORS(app)  

# Set up Google Vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secrets.json"
api_client = vision.ImageAnnotatorClient()


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
    # This is dumb, need to find a better way to detect names
    filter_terms = [
        "business",
        "world",
        "thru",
        "good",
        "valid",
        "visa",
        "credit",
        "union",
        "texas",
        "rewards",
        "american",
        "express",
        "master",
        "gold",
        "black",
        "discover",
        "bilt",
        "valid thru",
        "good thru",
    ]

    filtered_names = [
        name
        for name in cardholder_names
        if not any(term.lower() in name.lower() for term in filter_terms)
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
    cvv = cvv[0] if cvv else "000"
    if not cvv:
        errors.append("cvv")

    expiry_date = re.findall(r"\d{2}\/\d{2}", card_scan)
    expiry_date = expiry_date[-1] if expiry_date else None
    if not expiry_date:
        errors.append("expiry date")

    return cardholder_name, card_number, cvv, expiry_date, username, cardname, errors


@app.route("/api/scan", methods=["POST"])
def scan_card():
    """Handles image uploads and scans for credit card text."""

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    username = request.form.get("username", "default_user")
    cardname = request.form.get("cardname", "unnamed_card")

    image_content = file.read()
    text = detect_text(image_content)

    if not text:
        return jsonify({"error": "No text detected in image"}), 400

    card_info = parse_card_info(text, username, cardname)
    card_data = {
        "cardholder_name": card_info[0],
        "card_number": card_info[1],
        "cvv": card_info[2],
        "expiry_date": card_info[3],
        "username": card_info[4],
        "cardname": card_info[5],
    }

    print("🧠 Parsed card data:", card_data)

    # Send to the web app
    web_app_url = "http://127.0.0.1:5002/verify_info"  # ← updated for local use
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(web_app_url, json=card_data, headers=headers, timeout=5)
        if response.status_code == 200:
            return jsonify({"message": "Card scanned and saved successfully."}), 200
        return jsonify({"error": "Failed to save card via /verify_info"}), 500
    except Exception as e:
        print("❌ Error posting to web app:", str(e))
        return jsonify({"error": "Failed to communicate with web app."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)

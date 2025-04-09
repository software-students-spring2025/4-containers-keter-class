"""
Machine learning API and parsing and storage of credit card information
"""

import re
import os
import requests

from flask import Flask, request, jsonify, redirect
from google.cloud import vision  # pylint: disable=no-name-in-module

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secrets.json"
client = vision.ImageAnnotatorClient()


def detect_text(content):
    """Detects text in the file."""

    # with open(path, "rb") as image_file:
    #     content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)  # pylint: disable=no-member
    texts = response.text_annotations

    if response.error.message:
        raise RuntimeError(
            f"{response.error.message}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors"
        )

    if not texts:
        return ""

    print(texts[0].description)
    return texts[0].description


def parse_card_info(card_scan, username, cardname):
    """
    Breaks down text scan into card information

    Parameters:
    card_scan (str): text from ML image scan as a single line string
    username (str): website user identification (could be replaced with user_id or the likes)
    cardname (str): user chosen name for identifying multiple cards per user
    """

    errors = []

    cardholder_name = "CARDHOLDER NAME"
    cardholder_names = re.findall(
        r"\b[A-Z]+[a-z]*(?:\s+[A-Z]+[a-z]*\.?)?(?:\s+[A-Z]+[a-z]*)+\.?(?<!\bUS)\b",
        card_scan,
    )
    cardholder_names = [word for item in cardholder_names for word in item.split("\n")]

    # This is dumb, need to find a better way to detect names
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
                "BUSINESS",
                "DISCOVER",
                "BILT",
                "SEC CODE",
            ]
        )
    ]
    if filtered_names:
        cardholder_name = filtered_names[0]

    if len(filtered_names) != 1:
        errors.append("cardholder name")
        cardholder_name = None
        cardholder_name = filtered_names

    card_number = re.findall(r"\d{4} \d{4} \d{4} \d{4}", card_scan)
    if len(card_number) != 1:
        errors.append("card number")
        card_number = None
    else:
        card_number = card_number[0]

    cvv = re.findall(r"(?<![.-])\b\d{3}\b(?![.-]\d)", card_scan)
    if len(cvv) < 1:
        errors.append("cvv")
        cvv = None
    else:
        cvv = cvv[0]

    # there's a small little date at the top of the card, not sure what it is
    expiry_date = re.findall(r"\d{2}\/\d{2}", card_scan)
    if len(expiry_date) < 1:
        errors.append("expiry date")
        expiry_date = None
    else:
        expiry_date = expiry_date[-1]

    return cardholder_name, card_number, cvv, expiry_date, username, cardname, errors


@app.route("/api/scan", methods=["POST"])
def scan_card():
    """API endpoint to scan a credit card image."""

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    username = request.form.get("username", "default_user")
    cardname = request.form.get("cardname", "unnamed_card")

    image_content = file.read()
    text = (
        "realawesomebank.com 12345 AB 03/20 123456ABC "
        "1234 4321 1010 5454 Valid Thru: 01/26 Sec code: 123 "
        "JOHN JACOB JINGLEHEIMER SCHMIDT US and Canada 800.421.211 "
        "Int'l: 302-594-8200 Made from recycled plastic"
    )
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

    print(card_data)

    web_app_url = "http://web-app:5002/verify_info"  # Adjust the URL as needed
    headers = {"Content-Type": "application/json"}
    response = requests.post(web_app_url, json=card_data, headers=headers, timeout=5)

    if response.status_code == 200:
        return redirect(web_app_url)
    return jsonify({"error": "Failed to load verify_info page"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)

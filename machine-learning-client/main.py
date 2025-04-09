"""
Machine learning API and parsing and storage of credit card information
"""
import re
import os
from flask import Flask, request, jsonify
from google.cloud import vision

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="client_secrets.json"
client = vision.ImageAnnotatorClient()

def detect_text(content):
    """Detects text in the file."""

    # with open(path, "rb") as image_file:
    #     content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
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

# TEST_CARD_SCAN = (
#     "realawesomebank.com 12345 AB 03/20 123456ABC "
#     "1234 4321 1010 5454 Valid Thru: 01/26 Sec code: 123 "
#     "JOHN JACOB JINGLEHEIMER SCHMIDT US and Canada 800.421.211 "
#     "Int'l: 302-594-8200 Made from recycled plastic"
# )
# TEST_USERNAME = "j3schmidt"
# TEST_CARDNAME = "realawesomebank card 1"


def add_card_info(card_scan, username, cardname):
    """
    Breaks down text scan into card information and saves to MongoDB

    Parameters:
    card_scan (str): text from ML image scan as a single line string
    username (str): website user identification (could be replaced with user_id or the likes)
    cardname (str): user chosen name for identifying multiple cards per user
    """

    cardholder_name = "CARDHOLDER NAME"
    cardholder_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-z]+)+\b', card_scan)
    # This is dumb, need to find a better way to detect names
    filtered_names = [name for name in cardholder_names if not any(x in name for x in [
        "\n",
        "business", "WORLD", "THRU", "GOOD THRU", 
        "VALID THRU", "GOOD", "VISA", "CREDIT", "UNION", 
        "TEXAS", "REWARDS", "AMERICAN", "EXPRESS", "MASTER", 
        "GOLD", "BLACK", "BUSINESS", "DISCOVER", "BILT"
        ])]
    if filtered_names:
        cardholder_name = filtered_names[0]
    #assert len(cardholder_names) == 1, f"{len(cardholder_names)} card holders found"

    card_number = re.findall(r"\d{4} \d{4} \d{4} \d{4}", card_scan)
    #assert len(card_number) == 1, f"{len(card_number)} card numbers found"

    cvv = re.findall(r"(?<![.-])\b\d{3}\b(?![.-]\d)", card_scan)
    #assert len(cvv) == 1, f"{len(cvv)} cvvs found"
    if not cvv:
        cvv = "000"
    else:
        cvv = cvv[0]

    # there's a small little date at the top of the card, not sure what it is
    expiry_date = re.findall(r"\d{2}\/\d{2}", card_scan)
    #assert len(expiry_date) >= 1, "no expiry date found"

    card_number = card_number[0]
    expiry_date = expiry_date[-1]

    return cardholder_name, card_number, cvv, expiry_date, username, cardname

@app.route('/api/scan', methods=['POST'])
def scan_card():
    """API endpoint to scan a credit card image."""

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    username = request.form.get('username', 'default_user')
    cardname = request.form.get('cardname', 'unnamed_card')

    image_content = file.read()
    text = detect_text(image_content)

    if not text:
        return jsonify({'error': 'No text detected in image'}), 400

    card_info = add_card_info(text, username, cardname)

    card_data = {
        'cardholder_name': card_info[0],
        'card_number': card_info[1],
        'cvv': card_info[2],
        'expiry_date': card_info[3],
        'username': card_info[4],
        'cardname': card_info[5]
    }

    print(card_data)

    return jsonify({
        'success': True,
        'card_info': card_data
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)

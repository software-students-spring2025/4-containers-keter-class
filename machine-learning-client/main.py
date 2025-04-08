"""
Machine learning API and parsing and storage of credit card information
"""
import re
from web_app.app import create_app

card_collection = create_app().db.cards

TEST_CARD_SCAN = (
    "realawesomebank.com 12345 AB 03/20 123456ABC "
    "1234 4321 1010 5454 Valid Thru: 01/26 Sec code: 123 "
    "JOHN JACOB JINGLEHEIMER SCHMIDT US and Canada 800.421.211 "
    "Int'l: 302-594-8200 Made from recycled plastic"
)
TEST_USERNAME = "j3schmidt"
TEST_CARDNAME = "realawesomebank card 1"


def parse_card_info(card_scan, username, cardname):
    """
    Breaks down text scan into card information

    Parameters:
    card_scan (str): text from ML image scan as a single line string
    username (str): website user identification (could be replaced with user_id or the likes)
    cardname (str): user chosen name for identifying multiple cards per user
    """
    cardholder_name = re.findall(r"\b(?:[A-Z]+\.?\s+)+[A-Z]+\.?(?<!\bUS)\b", card_scan)
    assert len(cardholder_name) == 1, f"{len(cardholder_name)} card holders found"
    card_number = re.findall(r"\d{4} \d{4} \d{4} \d{4}", card_scan)
    assert len(card_number) == 1, f"{len(card_number)} card numbers found"
    cvv = re.findall(r"(?<![.-])\b\d{3}\b(?![.-]\d)", card_scan)
    assert len(cvv) == 1, f"{len(cvv)} cvvs found"
    # there's a small little date at the top of the card, not sure what it is
    expiry_date = re.findall(r"\d{2}\/\d{2}", card_scan)
    assert len(expiry_date) >= 1, "no expiry date found"
    cardholder_name = cardholder_name[0]
    card_number = card_number[0]
    cvv = cvv[0]
    expiry_date = expiry_date[-1]

    return cardholder_name, card_number, cvv, expiry_date, username, cardname


def add_card_info(card_scan, username, cardname):
    """
    Saves card information to MongoDB

    Parameters:
    card_scan (str): text from ML image scan as a single line string
    username (str): website user identification (could be replaced with user_id or the likes)
    cardname (str): user chosen name for identifying multiple cards per user
    """

    (
        cardholder_name,
        card_number,
        cvv,
        expiry_date,
        username,
        cardname,
    ) = parse_card_info(card_scan, username, cardname)

    card_collection.find_all(
        {
            "username": username,
            "cardname": cardname,
            "cardholder_name": cardholder_name,
            "card_number": card_number,
            "cvv": cvv,
            "expiry_date": expiry_date,
        }
    )
    if not card_collection.find_one({"username": username, "cardname": cardname}):
        card_collection.insert_one(
            {
                "username": username,
                "cardname": cardname,
                "cardholder_name": cardholder_name,
                "card_number": card_number,
                "cvv": cvv,
                "expiry_date": expiry_date,
            }
        )

    return card_collection.find_one({"username": username, "cardname": cardname})


def get_all_cards_from_user(username):
    """
    retrieve the names and numbers of all cards belonging to a specific user
    """

    all_cards = card_collection.find_many({"username": username})
    card_dict = {}
    if all_cards is not None:
        card_dict = {card["cardname"]: card["card_number"] for card in all_cards}
    return card_dict


def get_card_info(username, cardname):
    """
    retrieve the information for one card
    """
    return card_collection.find_one({"username": username, "cardname": cardname})


def delete_card(username, cardname):
    """
    remove a card from the database
    """
    card_collection.delete_one({"username": username, "cardname": cardname})


add_card_info(TEST_CARD_SCAN, TEST_USERNAME, TEST_CARDNAME)

for doc in card_collection.find():
    print(doc)

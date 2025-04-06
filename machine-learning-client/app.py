from pymongo import MongoClient
import re

client = MongoClient("mongodb://localhost:27017/")
# client = MongoClient("mongodb://mongodb:27017/") # use this once dockerized

db = client.credit_cards
collection = db.cards

test_card_scan = "realawesomebank.com 12345 AB 03/20 123456ABC 1234 4321 1010 5454 Valid Thru: 01/26 Sec code: 123 JOHN JACOB JINGLEHEIMER SCHMIDT US and Canada 800.421.211 Int'l: 302-594-8200 Made from recycled plastic"
test_username = "j3schmidt"
test_cardname = "realawesomebank card 1"

def add_card_info(card_scan, username, cardname):
    cardholder_name = re.findall(r"\b(?:[A-Z]+\.?\s+)+[A-Z]+\.?(?<!\bUS)\b", card_scan)
    assert len(cardholder_name) == 1, f"{len(cardholder_name)} card holders found"
    card_number = re.findall(r"\d{4} \d{4} \d{4} \d{4}", card_scan)
    assert len(card_number) == 1, f"{len(card_number)} card numbers found"
    cvv = re.findall(r"(?<![.-])\b\d{3}\b(?![.-]\d)", card_scan)
    assert len(cvv) == 1, f"{len(cvv)} cvvs found"
    expiry_date = re.findall(r"\d{2}\/\d{2}", card_scan) # there's a small little date at the top of the card, not sure what it is
    assert len(expiry_date) >= 1, f"no expiry date found"
    cardholder_name = cardholder_name[0]
    card_number = card_number[0]
    cvv = cvv[0]
    expiry_date = expiry_date[-1]

    collection.insert_one({"USERNAME": username,
                        "CARD NAME:": cardname,
                        "CARDHOLDER NAME": cardholder_name,
                        "CARD NUMBER": card_number,
                        "CVV": cvv, 
                        "EXPIRY DATE": expiry_date})
    return 
    
add_card_info(test_card_scan, test_username, test_cardname)
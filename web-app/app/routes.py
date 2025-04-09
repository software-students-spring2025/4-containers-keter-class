"""
Home to dashboard?
"""
import jsonify
import os
from flask import Flask, Blueprint, render_template, session, redirect, url_for, request

main = Blueprint("main", __name__)
from pymongo import MongoClient

app = Flask(__name__)


mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client.get_database()
card_collection = db.cards

@main.route("/")
def home():
    """
    docstring
    """
    if "user" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main.route("/dashboard")
def dashboard():
    """
    docstring
    """
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", user=session["user"])


@main.route("/verify_info", methods=["POST", "GET"])
def verify_info():
    """Manually verify information and get card nickname."""
    if request.method == "POST":
        print("POST request received with data:", request.form)
        card_data = {
            "cardholder_name": request.form["cardholder_name"],
            "card_number": request.form["card_number"],
            "cvv": request.form["cvv"],
            "expiry_date": request.form["expiry_date"],
            "username": request.form["username"],
            "cardname": request.form["cardname"]
        }
        return redirect(url_for("main.save_card_info"))

    else:
        data = request.get_json()
        print("GET request received with data:", data)
        if None in data:
            return render_template("scan_error.html", errors=data["errors"])
        return render_template("verify_info.html", **data)

@main.route("/api/save_card", methods=["POST"])
def save_card_info():
    """API endpoint to save card information to MongoDB."""
    data = card_collection.get_json()

    cardholder_name = data.get('cardholder_name')
    card_number = data.get('card_number')
    cvv = data.get('cvv')
    expiry_date = data.get('expiry_date')
    username = data.get('username')
    cardname = data.get('cardname')

    existing_card = card_collection.find_one({
        "username": username,
        "cardname": cardname
    })

    if existing_card:
        return jsonify({"error": "Card with this name already exists."}), 400

    card_collection.insert_one({
        "username": username,
        "cardname": cardname,
        "cardholder_name": cardholder_name,
        "card_number": card_number,
        "cvv": cvv,
        "expiry_date": expiry_date
    })

    return redirect(url_for('/dashboard'))

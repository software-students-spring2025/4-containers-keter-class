"""
Home to dashboard?
"""

import os
from flask import (
    Flask,
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
    jsonify,
)
from pymongo import MongoClient

main = Blueprint("main", __name__)


app = Flask(__name__)


mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client.get_database()
card_collection = db.cards


@main.route("/upload", methods=["GET"])
def upload():
    """
    Render the upload page where users can take a picture of a credit card.
    """
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("upload.html")


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
    Show all saved cards (for now, regardless of user).
    """
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    user = session.get("user")
    cards = list(card_collection.find({"username": user}))  # filter by user later

    return render_template("dashboard.html", user=user, cards=cards)


@main.route("/verify_info", methods=["POST", "GET"])
def verify_info():
    """Manually verify information and get card nickname."""

    if request.method == "POST":
        # Handle form submission
        if request.is_json:
            # If the request is JSON, parse it
            card_data = request.get_json()
        else:
            # Otherwise, it's form data, so retrieve it from the form
            card_data = {
                "cardholder_name": request.form.get("cardholder_name"),
                "card_number": request.form.get("card_number"),
                "cvv": request.form.get("cvv"),
                "expiry_date": request.form.get("expiry_date"),
                "username": request.form.get("username"),
                "cardname": request.form.get("cardname"),
            }

        existing_card = card_collection.find_one(
            {"username": card_data["username"], "cardname": card_data["cardname"]}
        )

        if existing_card:
            flash("Card with this name already exists.", "warning")
            return redirect(url_for("main.verify_info", **card_data))

        card_collection.insert_one(card_data)
        return redirect(url_for("main.dashboard"))

    card_data = {
        "cardholder_name": request.args.get("cardholder_name"),
        "card_number": request.args.get("card_number"),
        "cvv": request.args.get("cvv"),
        "expiry_date": request.args.get("expiry_date"),
        "username": request.args.get("username"),
        "cardname": request.args.get("cardname"),
    }

    # Validate if all necessary data was passed; otherwise, render an error page
    if None in card_data.values():
        errors = [field for field in card_data if card_data[field] is None]
        return render_template(
            "scan_error.html",
            errors=errors,
        )

    print("🛬 Received data at /verify_info (GET):", card_data)
    return render_template("verify_info.html", **card_data)


@main.route("/api/save_card", methods=["POST", "GET"])
def save_card_info():
    """API endpoint to save card information to MongoDB or handle redirect GET."""

    if request.method == "POST":
        data = request.get_json()

        print("💾 Saving card to DB:", data)

        cardholder_name = data.get("cardholder_name")
        card_number = data.get("card_number")
        cvv = data.get("cvv")
        expiry_date = data.get("expiry_date")
        username = data.get("username")
        cardname = data.get("cardname")

        existing_card = card_collection.find_one(
            {"username": username, "cardname": cardname}
        )

        if existing_card:
            return jsonify({"error": "Card with this name already exists."}), 400

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

        return redirect(url_for("main.dashboard"))

    return redirect(url_for("main.dashboard"))

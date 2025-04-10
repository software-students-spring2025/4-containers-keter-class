"""
Home to dashboard?
"""

import os
from flask import (
    Blueprint,
    render_template,
    session,
    redirect,
    url_for,
    request,
    flash,
)
from pymongo import MongoClient
from bson.objectid import ObjectId

main = Blueprint("main", __name__)

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
    Show all saved cards for each user.
    """
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    user = session.get("user")
    cards = list(card_collection.find({"username": user}))  # filter by user later

    return render_template("dashboard.html", user=user, cards=cards)


def get_card_data_from_request():
    """
    Parse card information from request
    """
    return {
        "cardholder_name": request.form.get("cardholder_name")
        or request.args.get("cardholder_name"),
        "card_number": request.form.get("card_number")
        or request.args.get("card_number"),
        "cvv": request.form.get("cvv") or request.args.get("cvv"),
        "expiry_date": request.form.get("expiry_date")
        or request.args.get("expiry_date"),
        "username": request.form.get("username") or request.args.get("username"),
        "cardname": request.form.get("cardname") or request.args.get("cardname"),
    }


@main.route("/verify_info", methods=["POST", "GET"])
def verify_info():
    """
    Manually verify information and get card nickname.
    Post information and save to mongodb
    """

    # Handle both GET and POST requests
    if request.method == "POST":
        if request.is_json:
            card_data = request.get_json()
        else:
            card_data = {
                "cardholder_name": request.form.get("cardholder_name"),
                "card_number": request.form.get("card_number"),
                "cvv": request.form.get("cvv"),
                "expiry_date": request.form.get("expiry_date"),
                "username": session.get("user"),
                "cardname": request.form.get("cardname"),
            }

        existing_card = card_collection.find_one(
            {"username": card_data["username"], "cardname": card_data["cardname"]}
        )

        if existing_card:
            flash("Card with this name already exists.", "warning")
            return redirect(url_for("main.verify_info", **card_data))

        card_collection.insert_one(card_data)
        session.pop("card_data", None)
        return redirect(url_for("main.dashboard"))

    # If it's a GET request, pull data from query parameters
    card_data = session.get("card_data")

    return render_template("verify_info.html", card_data=card_data)


@main.route("/retrieve", methods=["GET", "POST"])
def retrieve():
    """
    Receive card from request, determine if there are any issues
    If issues, go to scan_error, if not, go to verify_info
    For user verification
    """
    card_data = {
        "cardholder_name": request.args.get("cardholder_name"),
        "card_number": request.args.get("card_number"),
        "cvv": request.args.get("cvv"),
        "expiry_date": request.args.get("expiry_date"),
        "username": session.get("user"),
        "cardname": request.args.get("cardname"),
    }

    # Identify missing fields
    missing_fields = [key for key, val in card_data.items() if not val]

    # Store the card data in session
    session["card_data"] = card_data

    if missing_fields:
        # Include the missing fields in the redirect query string
        return redirect(
            url_for("main.scan_error", missing_fields=",".join(missing_fields))
        )

    return redirect(url_for("main.verify_info"))


@main.route("/scan_error", methods=["POST", "GET"])
def scan_error():
    """
    If information can't be correctly detected, redirect here
    Give option of retrying the scan or going to verify_info
    """
    if request.method == "POST":
        # Collect data from the form again on error handling
        card_data = get_card_data_from_request()

        # Store the updated card data in session
        session["card_data"] = card_data

        # Redirect to the verification page
        return redirect(url_for("main.verify_info"))

    # Extract errors from the query params
    errors = request.args.get("missing_fields", "").split(",")
    card_data = session.get("card_data", {})

    return render_template("scan_error.html", errors=errors, card_data=card_data)


@main.route("/delete_card/<card_id>", methods=["POST"])
def delete_card(card_id):
    """
    Delete a card from the database based on the card ID and user.
    """
    # Make sure the user is logged in
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    # Ensure the card exists in the database and belongs to the current user
    card = card_collection.find_one({"_id": ObjectId(card_id)})

    if not card:
        flash("Card not found.", "danger")
        return redirect(url_for("main.dashboard"))

    # Check if the logged-in user is the owner of the card
    if card["username"] != session.get("user"):
        flash("You are not authorized to delete this card.", "danger")
        return redirect(url_for("main.dashboard"))

    # Delete the card
    card_collection.delete_one({"_id": ObjectId(card_id)})

    flash("Card deleted successfully.", "success")
    return redirect(url_for("main.dashboard"))

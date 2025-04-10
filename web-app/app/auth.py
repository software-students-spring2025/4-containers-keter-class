"""
authorization including registration, login, lotgou
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
)
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Log in to existing account
    """
    if request.method == "POST":
        user = current_app.db.users.find_one({"username": request.form["username"]})
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user"] = user["username"]
            return redirect(url_for("main.dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Register new account
    """
    if request.method == "POST":
        existing = current_app.db.users.find_one({"username": request.form["username"]})
        if existing:
            flash("Username already registered.")
        else:
            hashed_pw = generate_password_hash(request.form["password"])
            current_app.db.users.insert_one(
                {"username": request.form["username"], "password": hashed_pw}
            )
            flash("Registered successfully. Please log in.")
            return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth.route("/logout")
def logout():
    """
    Log out of session
    """
    session.clear()
    return redirect(url_for("auth.login"))

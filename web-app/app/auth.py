from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import mongo

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = mongo.db.users.find_one({"email": request.form["email"]})
        if user and check_password_hash(user["password"], request.form["password"]):
            session["user"] = user["email"]
            return redirect(url_for("main.dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing = mongo.db.users.find_one({"email": request.form["email"]})
        if existing:
            flash("Email already registered.")
        else:
            hashed_pw = generate_password_hash(request.form["password"])
            mongo.db.users.insert_one({
                "email": request.form["email"],
                "password": hashed_pw
            })
            flash("Registered successfully. Please log in.")
            return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

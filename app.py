import os
import secrets
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("RENDER") == "true"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token

app.jinja_env.globals["csrf_token"] = csrf_token

@app.before_request
def verify_csrf():
    if request.method == "POST":
        expected = session.get("csrf_token")
        supplied = request.form.get("csrf_token")
        if not expected or not supplied or not secrets.compare_digest(expected, supplied):
            abort(400, description="Invalid or missing CSRF token.")

@app.route("/")
def index():
    user = db.session.get(User, session.get("user_id")) if session.get("user_id") else None
    return render_template("index.html", user=user)

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        errors = []
        if not 3 <= len(username) <= 30 or not username.replace("_", "").isalnum():
            errors.append("Username must be 3–30 characters and use letters, numbers, or underscores.")
        if "@" not in email or len(email) > 120:
            errors.append("Enter a valid email address.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("That username is already registered.")
        if User.query.filter_by(email=email).first():
            errors.append("That email is already registered.")
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("register.html", username=username, email=email)
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
        if not user or not user.check_password(password):
            flash("Invalid username/email or password.", "danger")
            return render_template("login.html", identifier=identifier)
        session.clear()
        session["user_id"] = user.id
        session["csrf_token"] = secrets.token_urlsafe(32)
        session.permanent = False
        flash("Welcome back! You are securely signed in.", "success")
        next_url = request.args.get("next") or url_for("dashboard")
        if not next_url.startswith("/") or next_url.startswith("//"):
            next_url = url_for("dashboard")
        return redirect(next_url)
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out securely.", "success")
    return redirect(url_for("index"))

@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", code=400, message=error.description), 400

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

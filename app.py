import os
import re
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
app.config["SESSION_COOKIE_NAME"] = "secureauth_session"
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

db = SQLAlchemy(app)
LOGIN_FAILURES = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 60

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

def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access that page.", "warning")
                return redirect(url_for("login", next=request.path))
            user = db.session.get(User, session["user_id"])
            if not user or user.role != role:
                abort(403, description="You do not have permission to access this resource.")
            return view(*args, **kwargs)
        return wrapped
    return decorator

def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token

def password_errors(password):
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if len(password) > 128:
        errors.append("Password must be 128 characters or fewer.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must include an uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must include a lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must include a number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append("Password must include a special character.")
    return errors

def client_key():
    return request.remote_addr or "unknown"

app.jinja_env.globals["csrf_token"] = csrf_token

@app.before_request
def verify_csrf():
    if request.method == "POST":
        expected = session.get("csrf_token")
        supplied = request.form.get("csrf_token")
        if not expected or not supplied or not secrets.compare_digest(expected, supplied):
            abort(400, description="Invalid or missing CSRF token.")

@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; script-src 'self'; "
        "img-src 'self' data:; form-action 'self'; frame-ancestors 'none'"
    )
    if request.is_secure:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

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
        if not 3 <= len(username) <= 30 or not re.fullmatch(r"[A-Za-z0-9_]+", username):
            errors.append("Username must be 3–30 characters and use letters, numbers, or underscores.")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(email) > 120:
            errors.append("Enter a valid email address.")
        errors.extend(password_errors(password))
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
        admin_email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        role = "admin" if admin_email and email == admin_email else "user"
        user = User(username=username, email=email, role=role)
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
        key = client_key()
        now = datetime.now(timezone.utc).timestamp()
        failures = [t for t in LOGIN_FAILURES.get(key, []) if now - t < LOCKOUT_SECONDS]
        if len(failures) >= MAX_LOGIN_ATTEMPTS:
            flash("Too many failed attempts. Please wait one minute before trying again.", "warning")
            return render_template("login.html", identifier=request.form.get("identifier", ""))
        identifier = request.form.get("identifier", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter((User.email == identifier) | (User.username == identifier)).first()
        if not user or not user.check_password(password):
            failures.append(now)
            LOGIN_FAILURES[key] = failures
            flash("Invalid username/email or password.", "danger")
            return render_template("login.html", identifier=identifier)
        LOGIN_FAILURES.pop(key, None)
        session.clear()
        session["user_id"] = user.id
        session["user_role"] = user.role
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

@app.route("/admin")
@role_required("admin")
def admin_dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin.html", users=users)

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have been logged out securely.", "success")
    return redirect(url_for("index"))

@app.errorhandler(400)
def bad_request(error):
    return render_template("error.html", code=400, message=error.description), 400

@app.errorhandler(403)
def forbidden(error):
    return render_template("error.html", code=403, message=error.description), 403

@app.errorhandler(413)
def too_large(error):
    return render_template("error.html", code=413, message="The submitted request is too large."), 413

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

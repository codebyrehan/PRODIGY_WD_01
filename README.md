# PRODIGY_WD_01 — Secure User Authentication System

A secure, responsive user authentication web application built for the Prodigy InfoTech Full-Stack Web Development Internship, Task 01.

## Features

- User registration with input validation
- Secure password hashing with Werkzeug
- Login with username or email
- Session-based authentication
- Protected dashboard route
- Logout and session clearing
- CSRF protection for POST requests
- Duplicate username/email checks
- Responsive UI
- Role field ready for future role-based access control

## Tech Stack

- Python / Flask
- Flask-SQLAlchemy
- SQLite
- HTML5 / CSS3 / JavaScript
- Gunicorn for production serving

## Run locally

```bash
python -m venv venv
# Windows PowerShell
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Security notes

Passwords are never stored in plain text. Session cookies use HttpOnly and SameSite protections, and production enables Secure cookies. Set a strong `SECRET_KEY` environment variable in production.

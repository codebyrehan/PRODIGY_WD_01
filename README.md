# PRODIGY_WD_01 — Secure User Authentication System

A secure, responsive user authentication web application built for the **Prodigy InfoTech Full-Stack Web Development Internship, Task 01**.

## Core requirements

- User registration with server-side validation
- Secure login with username or email
- Password hashing using Werkzeug
- Session-based authentication
- Protected dashboard route
- Secure logout and session clearing

## Enhanced features

- Strong password policy: 8–128 characters, uppercase, lowercase, number and special character
- Live password-strength requirement feedback on registration
- CSRF protection for every POST request
- Duplicate username/email protection
- Lightweight login throttling after repeated failed attempts
- Role-based access control with `user` and `admin` roles
- Protected admin dashboard for registered users
- Production security headers including CSP, HSTS on HTTPS, clickjacking protection and MIME sniffing protection
- Secure session-cookie configuration (`HttpOnly`, `SameSite`, `Secure` in production)
- Request-size limit
- Safe handling of post-login redirect targets
- Responsive UI and accessible form labels

## Tech Stack

- Python / Flask
- Flask-SQLAlchemy
- SQLite
- HTML5 / CSS3 / JavaScript
- Gunicorn for production serving
- Render Free for deployment

## Environment variables

- `SECRET_KEY` — set a strong random value in production
- `ADMIN_EMAIL` — optional email that receives the `admin` role when registering
- `RENDER=true` — enables production-only secure session cookie behavior

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

Passwords are never stored in plain text. Authentication uses hashed passwords and server-side sessions. All state-changing forms require a CSRF token. Login failures are throttled per client address. Production responses include additional browser security headers.

For a production system with multiple instances, the lightweight in-memory login throttling should be replaced by a shared store such as Redis, and database migrations should be managed with a migration tool such as Alembic/Flask-Migrate.

## Internship task mapping

This project satisfies Task 01 by implementing registration, secure login and protected routes, with optional security mechanisms and role-based access control added to demonstrate stronger full-stack/security practices.

# PRODIGY_WD_01 — SecureAuth

> **Prodigy InfoTech · Full-Stack Web Development Internship · Task 01**

SecureAuth is a professional, responsive authentication application built with Flask. It demonstrates secure registration, login, session-based authorization and protected routes, with additional security and UX features beyond the core internship brief.

## ✨ Features

### Authentication
- User registration with server-side validation
- Login with username **or** email
- Werkzeug password hashing — passwords are never stored in plain text
- Session-based authentication
- Secure logout and session clearing
- Protected user dashboard

### Security enhancements
- Strong password policy (8–128 chars, upper/lowercase, number, special character)
- CSRF protection on every state-changing POST request
- Duplicate username/email protection
- Login-attempt throttling
- Role-based access control (`user` / `admin`)
- Protected admin dashboard
- Secure cookie configuration (`HttpOnly`, `SameSite`, `Secure` on HTTPS)
- Content Security Policy and browser security headers
- HSTS when HTTPS is active
- Request-size limit
- Safe post-login redirect validation
- Custom 400 / 403 / 404 / 413 / 500 error pages

### UX
- Responsive desktop/mobile interface
- Clear validation and flash feedback
- Password requirement guidance
- Semantic form labels and keyboard-friendly controls
- Consistent visual design

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| ORM | Flask-SQLAlchemy |
| Database | SQLite (default) |
| Frontend | HTML5, CSS3, JavaScript |
| Security | Werkzeug hashing, CSRF tokens, secure cookies, CSP |
| Production server | Gunicorn |
| Deployment | Render Free |

## 🚀 Run locally

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## 🔐 Environment variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Strong random Flask session secret; set in production |
| `ADMIN_EMAIL` | Optional email that receives the `admin` role during registration |
| `DATABASE_URL` | Optional SQLAlchemy database URL |
| `RENDER` | Set to `true` for Render production behavior |

## 🧪 Recommended test flow

1. Open the registration page.
2. Create a valid account.
3. Verify weak passwords are rejected.
4. Log in using username and again using email.
5. Confirm `/dashboard` is inaccessible after logout.
6. Verify repeated invalid logins trigger throttling.
7. Verify a normal user cannot access `/admin`.
8. Register with `ADMIN_EMAIL` configured and verify admin access.
9. Try a nonexistent route and confirm the custom 404 page.

## 📌 Internship task mapping

The Prodigy InfoTech Task 01 brief requires a user authentication system with secure registration, login and protected routes. SecureAuth implements all of those requirements and adds the optional password hashing, session management and role-based access control mechanisms described in the brief.

## ⚠️ Production notes

The included login throttle is intentionally lightweight and process-local for this internship project. A multi-instance production deployment should move rate-limit state to a shared store such as Redis. Database schema changes should also use a migration system such as Alembic/Flask-Migrate rather than relying on `create_all()`.

---

**Built by Mohd Rehan · Full-Stack Web Development Internship · Prodigy InfoTech**

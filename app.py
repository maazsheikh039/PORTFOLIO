import os
import re
import sqlite3
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "messages.db")

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
if SMTP_PASSWORD:
    SMTP_PASSWORD = "".join(SMTP_PASSWORD.split())
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", SMTP_EMAIL)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
REQUIRE_EMAIL_DELIVERY = os.getenv("REQUIRE_EMAIL_DELIVERY", "true").lower() != "false"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_NAME_LENGTH = 80
MAX_EMAIL_LENGTH = 254
MAX_MESSAGE_LENGTH = 2000


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                email_sent INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )


def save_message(name, email, message, email_sent):
    created_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DATABASE) as conn:
        conn.execute(
            """
            INSERT INTO messages (name, email, message, email_sent, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, message, 1 if email_sent else 0, created_at),
        )


def send_email(name, sender_email, message):
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return False, "SMTP credentials not configured in .env"

    body = (
        f"New message from your portfolio contact form.\n\n"
        f"Name: {name}\n"
        f"Email: {sender_email}\n\n"
        f"Message:\n{message}\n"
    )

    msg = MIMEMultipart()
    msg["From"] = SMTP_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = f"Portfolio Contact: {name}"
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, RECEIVER_EMAIL, msg.as_string())
        return True, None
    except smtplib.SMTPException as exc:
        return False, str(exc)
    except OSError as exc:
        return False, str(exc)


init_db()


@app.after_request
def set_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()

    if not name or not email or not message:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    if (
        len(name) > MAX_NAME_LENGTH
        or len(email) > MAX_EMAIL_LENGTH
        or len(message) > MAX_MESSAGE_LENGTH
    ):
        return jsonify({"success": False, "error": "Please keep your message shorter."}), 400

    if not EMAIL_RE.match(email):
        return jsonify({"success": False, "error": "Please enter a valid email."}), 400

    email_sent, email_error = send_email(name, email, message)

    try:
        save_message(name, email, message, email_sent)
    except sqlite3.Error as exc:
        return jsonify({"success": False, "error": "Could not save your message."}), 500

    if email_sent:
        return jsonify({
            "success": True,
            "message": "Thank you! Your message has been sent.",
        })

    app.logger.warning("Contact form email failed: %s", email_error)

    if REQUIRE_EMAIL_DELIVERY:
        if not SMTP_EMAIL or not SMTP_PASSWORD:
            return jsonify({
                "success": False,
                "error": "Message saved, but email delivery is not configured yet.",
            }), 503

        return jsonify({
            "success": False,
            "error": "Message saved, but email delivery failed. Please email me directly.",
        }), 502

    return jsonify({
        "success": True,
        "message": "Thank you! Your message has been saved.",
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

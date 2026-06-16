import os
import sqlite3
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "messages.db")

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", SMTP_EMAIL)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/contact", methods=["POST"])
def contact():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    message = data.get("message", "").strip()

    if not name or not email or not message:
        return jsonify({"success": False, "error": "All fields are required."}), 400

    if "@" not in email or "." not in email.split("@")[-1]:
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

    if not SMTP_EMAIL or not SMTP_PASSWORD:
        return jsonify({
            "success": True,
            "message": "Thank you! Your message has been saved.",
        })

    app.logger.warning("Contact form email failed: %s", email_error)
    return jsonify({
        "success": True,
        "message": "Thank you! Your message has been saved.",
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

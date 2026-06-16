# Maaz Ghufran — Portfolio

Personal portfolio website built with Flask, HTML, CSS, and JavaScript.

## Run locally

```bash
cd /home/maaz/Projects/maaz-portfolio
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://localhost:5000](http://localhost:5000)

## Email setup (contact form → your Gmail)

1. Copy env template:
   ```bash
   cp .env.example .env
   ```
2. Google Account → **Security** → enable **2-Step Verification**
3. **App passwords** → create one for "Mail" → copy the 16-character password
4. Edit `.env`:
   ```
   SMTP_EMAIL=maazsheikh039@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx
   RECEIVER_EMAIL=maazsheikh039@gmail.com
   ```
5. Restart `python app.py` and test the contact form

Messages are also saved in `messages.db` (SQLite) as backup.

View saved messages:
```bash
sqlite3 messages.db "SELECT id, name, email, message, created_at FROM messages;"
```

## Add your photo

1. Save your photo as `static/images/profile.jpg`
2. Open `static/js/main.js` and uncomment the photo block at the bottom

## Add projects

Edit the Projects section in `templates/index.html` — replace placeholder cards with your real projects (title, description, tech tags, GitHub and demo links).

## Structure

```
maaz-portfolio/
├── app.py              # Flask backend
├── requirements.txt
├── templates/
│   └── index.html      # Main page
└── static/
    ├── css/style.css
    ├── js/main.js
    └── images/         # Add profile.jpg here
```
# PORTFOLIO

from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from hashing_service import get_image_hash  # Custom hashing function
from reverse_search import search_similar_images

app = Flask(__name__)

# --- Config ---
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

EMAIL_SENDER = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'

# --- Initialize DB ---
def init_db():
    with sqlite3.connect('uploads.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS uploads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        email TEXT NOT NULL,
                        image_hash TEXT NOT NULL)''')

        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
        conn.commit()

init_db()

# --- Email Notification ---
def send_notification(to_email, image_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = '🚨 Copyright Alert: Your Image Was Reuploaded'
        body = f"""
Hello,

Your previously uploaded image '{image_name}' has been uploaded again by someone.

Please review and take necessary actions.

— AI Copyright Protection System
"""
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"📧 Email sent to: {to_email}")

    except Exception as e:
        print(f"❌ Email sending failed: {e}")

# --- Routes ---
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/plagiarism')
def plagiarism():
    return render_template('plagiarism.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('uploads.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
            user = c.fetchone()

        if user:
            return redirect(url_for('plagiarism'))
        return render_template('signin.html', error="Invalid email or password.")
    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        with sqlite3.connect('uploads.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE email=?', (email,))
            if c.fetchone():
                return render_template('signup.html', error="Email already exists!")
            c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
        return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/analyse')
def analyse():
    return render_template('analyse.html')

@app.route('/check_plagiarism', methods=['POST'])
def check_plagiarism():
    print("📥 /check_plagiarism hit")

    if 'image' not in request.files or 'email' not in request.form:
        return jsonify({'message': '❌ Missing image or email.'}), 400

    file = request.files['image']
    email = request.form['email']

    if file.filename == '':
        return jsonify({'message': '❌ No file selected.'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        image_hash = get_image_hash(filepath)

        with sqlite3.connect('uploads.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM uploads WHERE image_hash=?', (image_hash,))
            match = c.fetchone()

            if match:
                owner_email = match[2]
                send_notification(owner_email, filename)
                os.remove(filepath)
                return jsonify({'message': f'⚠️ Duplicate image detected. Owner has been notified ({owner_email}).', 'status': 'duplicate'}), 200

            c.execute('INSERT INTO uploads (filename, email, image_hash) VALUES (?, ?, ?)',
                      (filename, email, image_hash))
            conn.commit()

        return jsonify({'message': '✅ Your image has been successfully uploaded and verified.', 'status': 'new'}), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'message': '❌ Server error. Please try again later.', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

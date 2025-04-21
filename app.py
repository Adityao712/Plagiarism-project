from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from hashing_service import get_image_hash  # Import hashing service

app = Flask(__name__)

# Upload Folder Setup
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('uploads.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            email TEXT NOT NULL,
            image_hash TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- Email Notification Setup ---
EMAIL_SENDER = 'your_email@gmail.com'
EMAIL_PASSWORD = 'your_app_password'  # Use an app password if using Gmail

# Send notification email
def send_notification(to_email, image_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = '🚨 Copyright Alert: Your Image Was Reuploaded'

        body = f"Hello,\n\nYour previously uploaded image '{image_name}' has been uploaded again.\n\nPlease review and take necessary actions.\n\n- AI Copyright Protection Team"
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)

        print("📬 Notification sent to", to_email)
    except Exception as e:
        print("❌ Failed to send email:", e)

# --- Routes ---
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('uploads.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('main'))
        else:
            return render_template('signin.html', error="Invalid email or password. Please try again.")

    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        conn = sqlite3.connect('uploads.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=?', (email,))
        existing_user = c.fetchone()

        if existing_user:
            return render_template('signup.html', error="Email already exists!")

        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    print("📩 Received request at /upload")

    if 'file' not in request.files or 'email' not in request.form:
        return jsonify({'message': '❌ Missing file or email'}), 400

    file = request.files['file']
    email = request.form['email']

    if file.filename == '':
        return jsonify({'message': '❌ No file selected'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        img_hash = get_image_hash(filepath)

        conn = sqlite3.connect('uploads.db')
        c = conn.cursor()
        c.execute('SELECT * FROM uploads WHERE image_hash = ?', (img_hash,))
        match = c.fetchone()

        if match:
            conn.close()
            os.remove(filepath)  # remove duplicate
            return jsonify({'message': '⚠️ Image already exists!', 'status': 'duplicate'}), 200

        c.execute('INSERT INTO uploads (filename, email, image_hash) VALUES (?, ?, ?)',
                  (filename, email, img_hash))
        conn.commit()
        conn.close()

        return jsonify({'message': '✅ File uploaded successfully!', 'status': 'new'}), 200

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({'message': '❌ Upload failed due to server error', 'error': str(e)}), 500


    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        img_hash = get_image_hash(filepath)

        conn = sqlite3.connect('uploads.db')
        c = conn.cursor()
        c.execute('SELECT * FROM uploads WHERE image_hash = ?', (img_hash,))
        match = c.fetchone()

        if match:
            original_email = match[2]
            send_notification(original_email, filename)
            conn.close()
            return jsonify({'message': '⚠️ Image already exists! Owner notified.', 'status': 'duplicate'}), 200

        c.execute('INSERT INTO uploads (filename, email, image_hash) VALUES (?, ?, ?)', (filename, email, img_hash))
        conn.commit()
        conn.close()

        return jsonify({'message': '✅ File uploaded successfully!', 'status': 'new'})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': '❌ Upload failed due to server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import sqlite3
from werkzeug.utils import secure_filename
from hashing_service import get_image_hash  # 👈 Import hashing service

# Initialize Flask App
app = Flask(__name__)

# Upload Folder Setup
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure uploads folder exists
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

# Call DB initialization once
init_db()

# --- Routes ---

# Landing Page
@app.route('/')
def landing():
    return render_template('landing.html')

# Sign-in Page
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
            error = "Invalid email or password. Please try again."
            return render_template('signin.html', error=error)

    return render_template('signin.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            error = "Passwords do not match!"
            return render_template('signup.html', error=error)

        conn = sqlite3.connect('uploads.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=?', (email,))
        existing_user = c.fetchone()

        if existing_user:
            error = "Email already exists!"
            return render_template('signup.html', error=error)

        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        conn.close()

        return redirect(url_for('signin'))

    return render_template('signup.html')

# Main Page (Upload interface)
@app.route('/main')
def main():
    return render_template('plagiarism.html')

# File Upload Route
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

        # 🔍 Get hash of the uploaded image
        img_hash = get_image_hash(filepath)

        # 🧠 Check if hash already exists
        conn = sqlite3.connect('uploads.db')
        c = conn.cursor()
        c.execute('SELECT * FROM uploads WHERE image_hash = ?', (img_hash,))
        match = c.fetchone()

        if match:
            conn.close()
            return jsonify({'message': '⚠️ Image already exists!', 'status': 'duplicate'}), 200

        # 📝 Save to database
        c.execute('INSERT INTO uploads (filename, email, image_hash) VALUES (?, ?, ?)', (filename, email, img_hash))
        conn.commit()
        conn.close()

        return jsonify({'message': '✅ File uploaded successfully!', 'status': 'new'})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': '❌ Upload failed due to server error'}), 500

# Run the server
if __name__ == '__main__':
    app.run(debug=True)

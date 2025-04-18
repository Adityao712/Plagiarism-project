from flask import Flask, request, jsonify, render_template
import os
import sqlite3
from werkzeug.utils import secure_filename

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
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Call DB initialization once
init_db()

# --- Routes ---

# Home route - renders HTML page
@app.route('/')
def index():
    return render_template('plagiarism.html')  # Make sure this is inside /templates
# Upload route - handles file & email
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

        # Insert into database
        conn = sqlite3.connect('uploads.db')
        c = conn.cursor()
        c.execute('INSERT INTO uploads (filename, email) VALUES (?, ?)', (filename, email))
        conn.commit()
        conn.close()

        return jsonify({'message': '✅ File uploaded successfully!'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': '❌ Upload failed due to server error'}), 500

# Run the server
if __name__ == '__main__':
    app.run(debug=True)

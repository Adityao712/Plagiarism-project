from flask import Blueprint, request, jsonify
from hashing_service import get_image_hash
import os
import sqlite3
from PIL import Image
import imagehash
from werkzeug.utils import secure_filename

upload_blueprint = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'uploads'
NEW_SUBMISSIONS_FOLDER = 'new_submissions'
DB_PATH = 'uploads.db'
SIMILARITY_THRESHOLD = 0.9  # 90%

# Create folders if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(NEW_SUBMISSIONS_FOLDER, exist_ok=True)

def compute_similarity(hash1, hash2):
    max_distance = len(bin(int(hash1))) - 2
    return 1 - (hash1 - hash2) / max_distance

def init_image_hash_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS image_hashes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    email TEXT NOT NULL,
                    hash TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

init_image_hash_table()

@upload_blueprint.route('/upload', methods=['POST'])
@upload_blueprint.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files or 'email' not in request.form:
            return jsonify({'message': '❌ File or email missing'}), 400

        file = request.files['file']
        email = request.form.get('email')
        filename = secure_filename(file.filename)

        if filename == '':
            return jsonify({'message': '❌ No file selected'}), 400

        temp_path = os.path.join('temp', filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_path)

        print(f"[INFO] File saved to temp: {temp_path}")

        # Load and hash
        image = Image.open(temp_path)
        new_hash = imagehash.phash(image)

        print(f"[INFO] Generated hash: {new_hash}")

        # Load existing hashes from DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT filename, hash FROM image_hashes")
        rows = c.fetchall()
        conn.close()

        matches = []
        for existing_filename, hash_str in rows:
            existing_hash = imagehash.hex_to_hash(hash_str)
            similarity = compute_similarity(new_hash, existing_hash)
            if similarity >= SIMILARITY_THRESHOLD:
                matches.append({
                    "filename": existing_filename,
                    "similarity": round(similarity * 100, 2)
                })

        if matches:
            os.remove(temp_path)
            print("[INFO] Match found:", matches)
            return jsonify({
                "message": "🛑 Similar image(s) found",
                "matches": matches
            })

        # No match – save and record hash
        new_path = os.path.join(NEW_SUBMISSIONS_FOLDER, filename)
        os.rename(temp_path, new_path)

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO image_hashes (filename, email, hash) VALUES (?, ?, ?)",
                  (filename, email, str(new_hash)))
        conn.commit()
        conn.close()

        print(f"[INFO] Stored new image at: {new_path}")
        return jsonify({
            "message": "✅ No similar image found. New image saved.",
            "location": new_path
        })

    except Exception as e:
        print("❌ Upload error:", str(e))
        return jsonify({'message': f'❌ Server error: {str(e)}'}), 500

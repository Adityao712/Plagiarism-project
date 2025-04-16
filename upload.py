from flask import Blueprint, request, jsonify
from firebase_service import db
from hashing_service import generate_file_hash
from plagiarism_check import check_text_plagiarism
import os

upload_blueprint = Blueprint('upload', __name__)
UPLOAD_FOLDER = 'uploads'

@upload_blueprint.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    user_email = request.form.get('email')

    # Save temporarily
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    file_hash = generate_file_hash(file_path)

    # Check if file already exists in Firebase
    existing = db.collection('files').where('hash', '==', file_hash).stream()
    if any(existing):
        return jsonify({"message": "❗ Already exists (possible plagiarism)."})

    # TEXT plagiarism check (optional for now)
    if file.filename.endswith('.txt'):
        with open(file_path, 'r') as f:
            text_data = f.read()
        plagiarism_result = check_text_plagiarism(text_data)
    else:
        plagiarism_result = {}

    # Store in Firebase
    db.collection('files').add({
        'email': user_email,
        'filename': file.filename,
        'hash': file_hash,
        'plagiarism_result': plagiarism_result
    })

    os.remove(file_path)
    return jsonify({"message": "✅ File saved & copyright claimed!", "plagiarism_result": plagiarism_result})

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv 
import os

load_dotenv()
app = Flask(__name__, static_url_path='/static')
CORS(app)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')  # ✅ Loaded from .env
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print("Upload folder from .env:", UPLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('plagiarism.html')  # Loads your HTML file

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    email = request.form.get('email')


    if not file or not email:
        return jsonify({'message': 'Missing file or email'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # You can plug your hashing/plagiarism code here

    return jsonify({'message': '✅ File received successfully!', 'filename': file.filename})

if __name__ == '__main__':
    app.run(debug=True)
    print(f"Saving file: {file.filename}")
#hahahaa ankit is gay 

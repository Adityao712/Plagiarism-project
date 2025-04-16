import os
from firebase_admin import credentials, initialize_app, firestore
from dotenv import load_dotenv

load_dotenv()
cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
initialize_app(cred)
db = firestore.client()

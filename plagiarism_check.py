import requests
import base64

def check_text_plagiarism(text_content):
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "email": "your_email@example.com",   # use your dev email
        "key": "your_copyleaks_api_key",     # get this from copyleaks.com
        "base64": base64.b64encode(text_content.encode()).decode(),
        "filename": "check.txt"
    }

    # For hackathon, mock this with a dummy response
    return {"plagiarized": False, "sources": []}

import requests

# Replace with your actual Bing Visual Search API key
BING_API_KEY = 'YOUR_API_KEY'
BING_SEARCH_ENDPOINT = 'https://api.bing.microsoft.com/v7.0/images/visualsearch'

def search_similar_images(image_path):
    headers = {'Ocp-Apim-Subscription-Key': BING_API_KEY}
    files = {'image': ('image.jpg', open(image_path, 'rb'))}

    response = requests.post(BING_SEARCH_ENDPOINT, headers=headers, files=files)

    if response.status_code != 200:
        return {'error': f"Failed to search image: {response.status_code}", 'status': 'fail'}

    results = response.json()
    matches = []

    try:
        tags = results.get("tags", [])
        for tag in tags:
            for action in tag.get("actions", []):
                if action.get("actionType") == "VisualSearch":
                    for item in action.get("data", {}).get("value", []):
                        matches.append(item.get("contentUrl"))
    except Exception as e:
        return {'error': str(e), 'status': 'fail'}

    return {'matches': matches, 'status': 'success'}

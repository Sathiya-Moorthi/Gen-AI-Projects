import requests
import json

url = "http://127.0.0.1:5000/update-notepad"
payload = {"date_time": "2023-10-27 12:00:00"}
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

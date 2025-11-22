import requests
import streamlit as st
import os

# In Docker, this will be the service name. Locally, localhost.
API_URL = os.getenv("API_URL", "http://localhost:5000/api/v1")

@st.cache_data(ttl=3600)
def get_supported_currencies():
    """Fetch available currencies from backend"""
    try:
        response = requests.get(f"{API_URL}/currencies")
        if response.status_code == 200:
            return response.json()['currencies']
        return ["USD", "EUR", "GBP", "INR"] # Fallback
    except Exception as e:
        st.error(f"Backend Connection Error: {e}")
        return []

def convert_currency(from_curr, to_curr, amount):
    """Post conversion request to backend"""
    payload = {
        "from_currency": from_curr,
        "to_currency": to_curr,
        "amount": amount
    }
    try:
        response = requests.post(f"{API_URL}/convert", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": response.text}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to backend."}
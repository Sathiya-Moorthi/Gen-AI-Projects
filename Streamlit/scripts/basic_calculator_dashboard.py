# frontend/dashboard.py
import streamlit as st
import requests

st.set_page_config(page_title="Flask + Streamlit Math App", page_icon="🧮")
st.title("🧮 Flask + Streamlit Math Calculator")

st.write("This app uses **Flask (Backend)** to perform calculations and **Streamlit (Frontend)** to display results interactively.")

# User inputs
a = st.number_input("Enter first number:", value=0.0)
b = st.number_input("Enter second number:", value=0.0)

# Dropdown for operations
operation = st.selectbox(
    "Choose an operation:",
    ["Add", "Subtract", "Multiply", "Divide", "Modulus", "Power"]
)

if st.button("Calculate"):
    # Convert to lowercase for API
    op = operation.lower()
    try:
        response = requests.get(f"http://127.0.0.1:5000/calculate?a={a}&b={b}&operation={op}")
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ Result: {data['result']}")
        else:
            st.error(f"❌ Error: {response.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"🚫 Could not connect to Flask API: {e}")

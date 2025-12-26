"""
frontend.py

Streamlit application for the Unit Conversion Application.
This serves as the user interface, interacting with the running Flask API
on localhost:5000 to perform and display conversions.
"""

import streamlit as st
import requests
from typing import Dict, Any

# --- Configuration ---
FLASK_API_URL = "http://localhost:5000/convert"

# Defined units and directions for the UI
UNITS_AND_DIRECTIONS = {
    "Currency": {
        "unit_type": "currency",
        "options": ["USD_to_INR", "INR_to_USD"]
    },
    "Temperature": {
        "unit_type": "temperature",
        "options": ["C_to_F", "F_to_C"]
    },
    "Length": {
        "unit_type": "length",
        "options": ["CM_to_INCH", "INCH_to_CM"]
    },
    "Weight": {
        "unit_type": "weight",
        "options": ["KG_to_LB", "LB_to_KG"]
    },
}

def call_api(payload: Dict[str, Any]) -> requests.Response:
    """Helper function to send POST request to the Flask API."""
    try:
        response = requests.post(FLASK_API_URL, json=payload, timeout=5)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        return response
    except requests.exceptions.HTTPError as e:
        # API returned an error response (e.g., 400 Bad Request)
        st.error(f"API Error ({e.response.status_code}): {e.response.json().get('error', 'Unknown API Error')}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("Connection Error: Could not connect to the Flask API. Please ensure 'app.py' is running on http://localhost:5000.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request Timeout: The Flask API took too long to respond.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Streamlit UI Layout ---

st.set_page_config(
    page_title="Microservice Unit Converter",
    layout="centered"
)

st.title("⚖️ Modular Unit Conversion App")
st.markdown("---")

# --- Sidebar for Unit Selection ---
st.sidebar.header("Configuration")
selected_unit = st.sidebar.selectbox(
    "Select Unit Type",
    list(UNITS_AND_DIRECTIONS.keys())
)

# Get configuration for the selected unit
config = UNITS_AND_DIRECTIONS[selected_unit]
unit_type = config["unit_type"]

st.sidebar.markdown("---")
# Radio buttons for Direction Selection
selected_direction = st.sidebar.radio(
    "Select Conversion Direction",
    config["options"],
)

# --- Main Conversion Interface ---

st.header(f"Convert: {selected_unit}")
st.subheader(f"Direction: `{selected_direction}`")

# Numeric Input
input_value = st.number_input(
    "Enter Value to Convert",
    value=1.0,
    format="%f"
)

# Conversion Button
if st.button("Convert", type="primary"):
    if input_value is None or input_value < 0 and unit_type != 'temperature':
        st.warning("Please enter a valid non-negative number.")
    else:
        # Prepare payload for the API
        payload = {
            "unit_type": unit_type,
            "direction": selected_direction,
            "value": float(input_value)
        }
        
        # Call the Flask API
        with st.spinner("Calculating result..."):
            response = call_api(payload)
        
        # Process the successful response
        if response and response.status_code == 200:
            result_data = response.json()
            
            # Format display strings for better readability
            input_label, output_label = selected_direction.split('_to_')
            
            st.success("Conversion Successful!")
            
            col1, col2 = st.columns(2)
            
            col1.metric(
                label=f"Input ({input_label})",
                value=f"{result_data['input_value']:.4f}"
            )
            col2.metric(
                label=f"Output ({output_label})",
                value=f"{result_data['converted_value']:.4f}"
            )

st.markdown("---")
st.caption(f"Backend API URL: `{FLASK_API_URL}`")
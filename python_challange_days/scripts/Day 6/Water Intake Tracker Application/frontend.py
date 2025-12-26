import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Configuration ---
API_URL = "http://127.0.0.1:5000"
st.set_page_config(page_title="HydroTrack", layout="wide")

# --- Custom CSS for "Clean/Modern" look ---
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def get_summary():
    """Fetch today's stats from Flask."""
    try:
        response = requests.get(f"{API_URL}/summary")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        return None
    return None

def log_water(amount):
    """Send water log to Flask."""
    try:
        payload = {"amount": int(amount)}
        response = requests.post(f"{API_URL}/log", json=payload)
        return response.status_code == 201
    except Exception as e:
        return False

def get_history():
    """Fetch 7-day history for charting."""
    try:
        response = requests.get(f"{API_URL}/history")
        if response.status_code == 200:
            return response.json()
    except:
        return []

# --- UI Layout ---

st.title("💧 Smart Hydration Tracker")
st.markdown("### Monitor your daily water intake")

# Check backend connection first
summary_data = get_summary()

if not summary_data:
    st.error("🚨 Error: Cannot connect to Backend API. Is 'backend.py' running?")
    st.stop()

# 1. Top Section: Metrics & Input
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Log Intake")
    # Buttons for quick entry
    with st.form("log_form"):
        amount = st.selectbox("Select Amount (ml)", [250, 330, 500, 750, 1000])
        submitted = st.form_submit_button("Add Water")
        
        if submitted:
            success = log_water(amount)
            if success:
                st.success(f"Added {amount}ml!")
                st.rerun() # Refresh to update metrics
            else:
                st.error("Failed to log water.")

with col2:
    st.subheader("Today's Progress")
    
    # Metrics Display
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Intake", f"{summary_data['total_ml']} ml")
    m2.metric("Daily Goal", f"{summary_data['goal_ml']} ml")
    m3.metric("Remaining", f"{max(summary_data['goal_ml'] - summary_data['total_ml'], 0)} ml")
    
    # Progress Bar
    st.progress(summary_data['percentage'] / 100)
    
    if summary_data['total_ml'] >= summary_data['goal_ml']:
        st.balloons()
        st.success("🎉 You reached your daily goal!")

st.divider()

# 2. Bottom Section: Visualization
st.subheader("Weekly Hydration Trend")

history_data = get_history()
if history_data:
    # Convert JSON list to Pandas DataFrame
    df = pd.DataFrame(history_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    # Group by day for the chart
    daily_stats = df.groupby('date')['amount_ml'].sum().reset_index()
    
    # Plotly Chart
    fig = px.bar(daily_stats, x='date', y='amount_ml', 
                 labels={'amount_ml': 'Volume (ml)', 'date': 'Date'},
                 title="Last 7 Days Intake")
    # Add a goal line to the chart
    fig.add_hline(y=3000, line_dash="dash", line_color="green", annotation_text="Daily Goal")
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No historical data available yet.")
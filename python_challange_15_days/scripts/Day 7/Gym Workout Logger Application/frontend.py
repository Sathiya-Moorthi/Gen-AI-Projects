# frontend.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Gym Workout Logger", layout="wide")
st.title("🏋️ Gym Workout Logger")

# --- Sidebar: Add New Log ---
st.sidebar.header("Log New Workout")
with st.sidebar.form("workout_form"):
    exercise_name = st.text_input("Exercise Name", placeholder="e.g., Bench Press")
    sets = st.number_input("Sets", min_value=1, value=3)
    reps = st.number_input("Reps", min_value=1, value=10)
    weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=20.0, step=0.5)
    submit_button = st.form_submit_button("Log Workout")

if submit_button:
    if not exercise_name:
        st.sidebar.error("Please enter an exercise name.")
    else:
        payload = {"exercise_name": exercise_name, "sets": sets, "reps": reps, "weight_kg": weight_kg}
        try:
            resp = requests.post(f"{API_URL}/log", json=payload)
            if resp.status_code == 201:
                st.sidebar.success("Workout saved!")
            else:
                st.sidebar.error(f"Error: {resp.json().get('error')}")
        except requests.exceptions.ConnectionError:
            st.sidebar.error("🚨 Backend offline.")

# --- Helper Functions ---
def fetch_data(endpoint, params=None):
    try:
        resp = requests.get(f"{API_URL}/{endpoint}", params=params)
        if resp.status_code == 200:
            return resp.json()
        return []
    except requests.exceptions.ConnectionError:
        return []

def calculate_1rm(weight, reps):
    if reps == 1: return weight
    return weight * (1 + (reps / 30))

# --- Main Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Progress Trends", "📝 Workout History", "💪 1RM Calculator"])

history_data = fetch_data("history")

# --- Tab 1: Progress Trends ---
with tab1:
    st.subheader("Volume Progression")
    if history_data:
        unique_exercises = sorted(list(set(item['exercise_name'] for item in history_data)))
        selected_exercise = st.selectbox("Filter by Exercise:", ["All Exercises"] + unique_exercises)
        
        if selected_exercise == "All Exercises":
            progress_data = fetch_data("progress")
            chart_title = "Total Volume (All Exercises)"
        else:
            progress_data = fetch_data("progress", params={"exercise": selected_exercise})
            chart_title = f"Volume Trend: {selected_exercise}"

        if progress_data:
            df_progress = pd.DataFrame(progress_data)
            fig = px.line(
                df_progress, x='date', y='total_volume', 
                title=chart_title, markers=True,
                labels={'total_volume': 'Volume (kg)', 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No data found for {selected_exercise}.")
    else:
        st.warning("Backend is offline or database is empty.")

# --- Tab 2: Workout History & Export ---
with tab2:
    st.subheader("Detailed Logs & Export")
    
    if history_data:
        df_history = pd.DataFrame(history_data)
        
        # --- NEW: Export Section ---
        col1, col2 = st.columns([1, 4]) # Create columns to align button nicely
        with col1:
            # Convert DataFrame to CSV
            csv = df_history.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="gym_workout_history.csv",
                mime="text/csv",
                help="Click to download your full workout history as a CSV file."
            )
        
        # Display Table
        st.dataframe(
            df_history[["date", "exercise_name", "sets", "reps", "weight_kg", "volume"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No history available to export.")

# --- Tab 3: 1RM Calculator ---
with tab3:
    st.header("One-Rep Max (1RM) Estimator")
    
    st.subheader("🧮 Quick Calculator")
    col1, col2 = st.columns(2)
    with col1:
        calc_weight = st.number_input("Lifted Weight (kg)", value=60.0, step=2.5)
    with col2:
        calc_reps = st.number_input("Reps Performed", value=5, step=1, min_value=1)
    
    estimated_max = calculate_1rm(calc_weight, calc_reps)
    st.success(f"🏆 Estimated 1RM: **{estimated_max:.2f} kg**")
    
    st.divider()
    
    st.subheader("🥇 Your Estimated Personal Records")
    if history_data:
        df_prs = pd.DataFrame(history_data)
        df_prs['estimated_1rm'] = df_prs.apply(lambda x: calculate_1rm(x['weight_kg'], x['reps']), axis=1)
        idx = df_prs.groupby('exercise_name')['estimated_1rm'].idxmax()
        best_lifts = df_prs.loc[idx].sort_values(by='estimated_1rm', ascending=False)
        
        st.dataframe(
            best_lifts[['exercise_name', 'date', 'weight_kg', 'reps', 'estimated_1rm']],
            column_config={
                "exercise_name": "Exercise", "date": "Date", "weight_kg": "Weight",
                "reps": "Reps", "estimated_1rm": st.column_config.NumberColumn("Est. 1RM", format="%.2f kg")
            },
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Log workouts to see PRs.")
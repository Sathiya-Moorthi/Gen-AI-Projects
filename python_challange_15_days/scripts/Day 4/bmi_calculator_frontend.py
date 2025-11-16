import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="BMI Calculator",
    page_icon="🏋️",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .bmi-result {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .underweight { background-color: #e3f2fd; border-left: 5px solid #2196f3; }
    .normal { background-color: #e8f5e8; border-left: 5px solid #4caf50; }
    .overweight { background-color: #fff3e0; border-left: 5px solid #ff9800; }
    .obese { background-color: #ffebee; border-left: 5px solid #f44336; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏋️ BMI Calculator</div>', unsafe_allow_html=True)

# Input form
with st.form("bmi_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        height = st.number_input(
            "Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=170.0,
            step=0.1,
            help="Enter your height in centimeters"
        )
    
    with col2:
        weight = st.number_input(
            "Weight (kg)", 
            min_value=10.0,
            max_value=300.0,
            value=65.0,
            step=0.1,
            help="Enter your weight in kilograms"
        )
    
    calculate_btn = st.form_submit_button("Calculate BMI", type="primary")

# BMI calculation and display
if calculate_btn:
    if height > 0 and weight > 0:
        try:
            # Call backend API
            response = requests.post(
                'http://localhost:5000/calculate-bmi',
                json={'height': height, 'weight': weight}
            )
            
            if response.status_code == 200:
                result = response.json()
                bmi = result['bmi']
                category = result['category']
                
                # Display results
                st.success("BMI calculated successfully!")
                
                # Color-coded result box
                category_class = category.lower()
                st.markdown(f"""
                <div class="bmi-result {category_class}">
                    <h3>Results:</h3>
                    <p><strong>BMI Value:</strong> {bmi}</p>
                    <p><strong>Category:</strong> {category}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # BMI progress bar
                st.subheader("BMI Scale")
                bmi_progress = min(bmi / 40, 1.0)  # Normalize for display
                st.progress(bmi_progress)
                
                # BMI categories explanation
                st.markdown("""
                **BMI Categories:**
                - **Underweight:** Below 18.5
                - **Normal:** 18.5 - 24.9  
                - **Overweight:** 25 - 29.9
                - **Obese:** 30 and above
                """)
                
            else:
                error_msg = response.json().get('error', 'Unknown error occurred')
                st.error(f"Error: {error_msg}")
                
        except requests.exceptions.RequestException:
            st.error("Backend service unavailable. Please ensure the Flask server is running.")
    else:
        st.warning("Please enter valid positive values for height and weight.")

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About BMI")
    st.markdown("""
    Body Mass Index (BMI) is a measure of body fat based on:
    
    **Formula:**
    ```
    BMI = weight (kg) / (height (m)²)
    ```
    
    **Note:** BMI is a screening tool, not a diagnostic of body fatness or health.
    """)
    
    st.header("⚙️ Setup Instructions")
    st.markdown("""
    1. Start backend: `python bmi_backend.py`
    2. Start frontend: `streamlit run bmi_frontend.py`
    3. Open browser to: `http://localhost:8501`
    """)
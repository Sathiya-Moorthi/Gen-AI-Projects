import streamlit as st
import requests
import time
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Coconut Farmers Registry",
    page_icon="🥥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stButton > button {
        width: 100%;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .warning-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .coconut-animation {
        font-family: monospace;
        text-align: center;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        border: 1px solid #e9ecef;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'submitted': False,
        'farmer_data': None,
        'api_status': "unknown",
        'current_mode': "register",  # "register" or "update"
        'all_farmers': [],
        'selected_farmer_id': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def check_api_health():
    """Check if the Flask API is running"""
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        st.session_state.api_status = "healthy" if response.status_code == 200 else "unhealthy"
        if st.session_state.api_status == "healthy":
            st.session_state.health_data = response.json()
    except requests.exceptions.RequestException:
        st.session_state.api_status = "unreachable"

def load_all_farmers():
    """Load all farmers from API"""
    try:
        response = requests.get("http://localhost:5000/api/farmers", timeout=5)
        if response.status_code == 200:
            data = response.json()
            st.session_state.all_farmers = data.get("farmers", [])
            return True
    except requests.exceptions.RequestException:
        st.session_state.all_farmers = []
    return False

def coconut_animation():
    """Display coconut falling animation"""
    st.markdown("---")
    st.subheader("🎉 Welcome to the Coconut Family!")
    
    animation_placeholder = st.empty()
    coconut = "🥥"
    palm_tree = "🌴"
    ground = "🟫" * 10
    
    # Animation sequence
    positions = [1, 2, 3, 2, 1]  # Falling pattern
    for pos in positions:
        animation_text = palm_tree + "\n"
        for i in range(3):
            if i == pos:
                animation_text += "  " + coconut + "\n"
            else:
                animation_text += "   \n"
        animation_text += ground
        animation_placeholder.markdown(f"<div class='coconut-animation'>{animation_text}</div>", unsafe_allow_html=True)
        time.sleep(0.4)
    
    # Final static position
    final_animation = f"""
    {palm_tree}
      {coconut}
    
    {ground}
    """
    animation_placeholder.markdown(f"<div class='coconut-animation'>{final_animation}</div>", unsafe_allow_html=True)

def show_registration_form():
    """Show farmer registration form"""
    st.subheader("📝 Register New Farmer")
    
    with st.form("farmer_registration_form", clear_on_submit=True):
        name = st.text_input(
            "Full Name *",
            placeholder="Enter your full name",
            help="Please enter your complete name as per official records"
        )
        
        age = st.slider(
            "Age *",
            min_value=18,
            max_value=80,
            value=35,
            help="Must be between 18 and 80 years"
        )
        
        # Age category indicator
        if age <= 25:
            age_category = "🌱 Young Farmer (18-25)"
        elif age <= 40:
            age_category = "🌴 Prime Farmer (26-40)" 
        elif age <= 60:
            age_category = "🌳 Experienced Farmer (41-60)"
        else:
            age_category = "🎖️ Veteran Farmer (61-80)"
        
        st.caption(f"Category: {age_category}")
        
        submitted = st.form_submit_button("🌴 Register My Farm")
        
        if submitted:
            if not name:
                st.error("❌ Please enter your name")
                return
                
            if len(name.strip()) < 2:
                st.error("❌ Name must be at least 2 characters long")
                return
            
            with st.spinner("Registering your farm..."):
                try:
                    response = requests.post(
                        "http://localhost:5000/api/farmer",
                        json={"name": name.strip(), "age": age},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        st.session_state.submitted = True
                        st.session_state.farmer_data = response.json()
                        st.session_state.current_mode = "register"
                        st.rerun()
                    elif response.status_code == 409:
                        error_data = response.json()
                        st.warning(f"⚠️ {error_data['error']}")
                        st.info(f"Existing Farmer ID: {error_data['existing_farmer_id']}")
                        if st.button("Switch to Update Mode"):
                            st.session_state.current_mode = "update"
                            st.session_state.selected_farmer_id = error_data['existing_farmer_id']
                            st.rerun()
                    else:
                        error_data = response.json()
                        st.error(f"❌ Registration failed: {error_data.get('error', 'Unknown error')}")
                        
                except requests.exceptions.RequestException as e:
                    st.error("❌ Connection error: Please check if the backend server is running")

def show_update_form():
    """Show farmer update form"""
    st.subheader("✏️ Update Existing Farmer")
    
    # Load farmers for selection
    if not st.session_state.all_farmers:
        st.warning("No farmers found in the database.")
        if st.button("Register New Farmer Instead"):
            st.session_state.current_mode = "register"
            st.rerun()
        return
    
    # Farmer selection
    farmer_options = {f"{f['id']}: {f['name']} (Age: {f['age']})": f['id'] 
                     for f in st.session_state.all_farmers}
    
    selected_farmer_label = st.selectbox(
        "Select Farmer to Update",
        options=list(farmer_options.keys()),
        index=0 if not st.session_state.selected_farmer_id else None,
        help="Choose a farmer from the database to update their information"
    )
    
    selected_farmer_id = farmer_options[selected_farmer_label]
    
    # Get current farmer data
    try:
        response = requests.get(f"http://localhost:5000/api/farmer/{selected_farmer_id}", timeout=5)
        if response.status_code == 200:
            current_data = response.json()["farmer_data"]
        else:
            st.error("Failed to load farmer data")
            return
    except requests.exceptions.RequestException:
        st.error("Failed to connect to server")
        return
    
    # Update form
    with st.form("farmer_update_form"):
        st.markdown(f"**Currently editing:** {current_data['name']} (ID: {current_data['id']})")
        
        new_name = st.text_input(
            "Full Name *",
            value=current_data["name"],
            help="Update the farmer's name"
        )
        
        new_age = st.slider(
            "Age *",
            min_value=18,
            max_value=80,
            value=current_data["age"],
            help="Update the farmer's age"
        )
        
        # Display current information
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Experience", current_data["experience_level"])
        with col2:
            st.metric("Registration Date", 
                     datetime.fromisoformat(current_data["registration_date"]).strftime("%Y-%m-%d"))
        
        submitted = st.form_submit_button("💾 Update Farmer Data")
        
        if submitted:
            if not new_name:
                st.error("❌ Please enter a name")
                return
                
            if len(new_name.strip()) < 2:
                st.error("❌ Name must be at least 2 characters long")
                return
            
            update_data = {}
            if new_name != current_data["name"]:
                update_data["name"] = new_name.strip()
            if new_age != current_data["age"]:
                update_data["age"] = new_age
            
            if not update_data:
                st.info("ℹ️ No changes detected. Please modify name or age to update.")
                return
            
            with st.spinner("Updating farmer data..."):
                try:
                    response = requests.put(
                        f"http://localhost:5000/api/farmer/{selected_farmer_id}",
                        json=update_data,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        st.session_state.submitted = True
                        st.session_state.farmer_data = response.json()
                        st.session_state.current_mode = "update"
                        st.rerun()
                    else:
                        error_data = response.json()
                        st.error(f"❌ Update failed: {error_data.get('error', 'Unknown error')}")
                        
                except requests.exceptions.RequestException as e:
                    st.error("❌ Connection error: Please check if the backend server is running")

def show_success_message():
    """Show success message after registration or update"""
    farmer_data = st.session_state.farmer_data
    
    if st.session_state.current_mode == "register":
        st.balloons()
        st.markdown(f"""
        <div class='success-message'>
            <h3>✅ Registration Successful!</h3>
            <p><strong>{farmer_data['message']}</strong></p>
            <p>Farmer ID: <code>{farmer_data['farmer_id']}</code></p>
            <p>Registration Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Coconut animation for new registrations
        coconut_animation()
        
    else:  # update mode
        st.success("✅ Update Successful!")
        st.markdown(f"""
        <div class='info-message'>
            <h3>📋 Farmer Data Updated</h3>
            <p><strong>{farmer_data['message']}</strong></p>
            <p>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Community benefits
    st.markdown("---")
    st.subheader("🎁 Community Benefits")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📚 Knowledge**")
        st.caption("Access farming guides and best practices")
        
    with col2:
        st.markdown("**🤝 Network**") 
        st.caption("Connect with fellow coconut growers")
        
    with col3:
        st.markdown("**🌱 Resources**")
        st.caption("Get discounts on farming supplies")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 Register Another Farmer", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.farmer_data = None
            st.session_state.current_mode = "register"
            st.rerun()
    with col2:
        if st.button("✏️ Update Another Farmer", use_container_width=True):
            st.session_state.submitted = False
            st.session_state.farmer_data = None
            st.session_state.current_mode = "update"
            st.rerun()

def show_database_stats():
    """Show database statistics in sidebar"""
    try:
        response = requests.get("http://localhost:5000/api/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # FIXED: Check if 'statistics' key exists in response
            if 'statistics' in data:
                stats = data['statistics']
            else:
                # If no statistics key, create default stats
                stats = {
                    "total_farmers": 0,
                    "average_age": 0,
                    "age_groups": {
                        "young": 0,
                        "prime": 0,
                        "experienced": 0,
                        "veteran": 0
                    }
                }
            
            st.sidebar.markdown("---")
            st.sidebar.subheader("📊 Community Stats")
            
            st.sidebar.metric("Total Farmers", stats["total_farmers"])
            if stats["total_farmers"] > 0:
                st.sidebar.metric("Average Age", f"{stats['average_age']} years")
            else:
                st.sidebar.metric("Average Age", "0 years")
            
            if stats["total_farmers"] > 0:
                st.sidebar.markdown("**Age Distribution:**")
                total = max(stats["total_farmers"], 1)  # Avoid division by zero
                st.sidebar.progress(stats["age_groups"]["young"] / total, 
                                  text="🌱 Young: {}".format(stats["age_groups"]["young"]))
                st.sidebar.progress(stats["age_groups"]["prime"] / total, 
                                  text="🌴 Prime: {}".format(stats["age_groups"]["prime"]))
                st.sidebar.progress(stats["age_groups"]["experienced"] / total, 
                                  text="🌳 Experienced: {}".format(stats["age_groups"]["experienced"]))
                st.sidebar.progress(stats["age_groups"]["veteran"] / total, 
                                  text="🎖️ Veteran: {}".format(stats["age_groups"]["veteran"]))
            else:
                st.sidebar.info("No farmers registered yet")
            
    except requests.exceptions.RequestException:
        st.sidebar.warning("Stats unavailable")
    except KeyError as e:
        st.sidebar.error(f"Error loading stats: {e}")
    except Exception as e:
        st.sidebar.error(f"Unexpected error: {e}")

def main():
    """Main application function"""
    initialize_session_state()
    check_api_health()
    load_all_farmers()
    
    # Sidebar
    with st.sidebar:
        st.title("🥥 Coconut Registry")
        
        # Mode selection
        st.subheader("Navigation")
        mode = st.radio(
            "Choose Action:",
            ["Register New Farmer", "Update Existing Farmer", "View Database"],
            index=0 if st.session_state.current_mode == "register" else 1
        )
        
        if "Register" in mode:
            st.session_state.current_mode = "register"
        elif "Update" in mode:
            st.session_state.current_mode = "update"
        else:
            st.session_state.current_mode = "view"
        
        # API status
        status_color = {
            "healthy": "🟢",
            "unhealthy": "🟡", 
            "unreachable": "🔴",
            "unknown": "⚫"
        }
        st.sidebar.caption(f"API Status: {status_color[st.session_state.api_status]} {st.session_state.api_status}")
        
        if st.session_state.api_status == "unreachable":
            st.sidebar.error("Backend server not running")
            st.sidebar.info("Start with: `python api.py`")
        
        # Database statistics
        if st.session_state.api_status == "healthy":
            show_database_stats()
    
    # Main content
    st.title("🌴 Coconut Farmers Registry")
    
    if st.session_state.api_status == "unreachable":
        st.error("⚠️ Unable to connect to registration service. Please ensure the backend server is running.")
        st.info("To start the backend server, run: `python api.py` in your terminal.")
        return
    
    # Display appropriate content based on mode and submission status
    if st.session_state.submitted:
        show_success_message()
    else:
        if st.session_state.current_mode == "register":
            show_registration_form()
        elif st.session_state.current_mode == "update":
            show_update_form()
        else:  # view mode
            st.subheader("👥 Registered Farmers")
            
            if not st.session_state.all_farmers:
                st.info("No farmers registered yet. Be the first to register!")
            else:
                for farmer in st.session_state.all_farmers:
                    with st.expander(f"👨‍🌾 {farmer['name']} (Age: {farmer['age']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**ID:** {farmer['id']}")
                            st.write(f"**Experience:** {farmer['experience_level']}")
                            st.write(f"**Specializes in:** {farmer.get('coconut_type', 'coconuts')}")
                        with col2:
                            reg_date = datetime.fromisoformat(farmer['registration_date']).strftime("%Y-%m-%d")
                            st.write(f"**Registered:** {reg_date}")
                            if farmer.get('last_updated') != farmer['registration_date']:
                                update_date = datetime.fromisoformat(farmer['last_updated']).strftime("%Y-%m-%d")
                                st.write(f"**Last Updated:** {update_date}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🌴 Built for Coconut Farmers Worldwide 🥥<br>"
        "<small>Supporting sustainable coconut farming</small>"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
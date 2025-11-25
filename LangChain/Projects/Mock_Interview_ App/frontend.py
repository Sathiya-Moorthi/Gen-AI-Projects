"""
Frontend module for Mock Interview Chatbot using Streamlit.
Provides the user interface for conducting mock interviews.
"""

import streamlit as st
from backend import InterviewBot
from config import Config
from datetime import datetime


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "interview_bot" not in st.session_state:
        st.session_state.interview_bot = None
    
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "selected_role" not in st.session_state:
        st.session_state.selected_role = None
    
    if "awaiting_answer" not in st.session_state:
        st.session_state.awaiting_answer = False


def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            background-color: #f5f7fa;
        }
        
        /* Chat message styling - Dark mode compatible */
        .stChatMessage {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: #262730 !important;
        }
        
        /* Dark mode chat message styling */
        @media (prefers-color-scheme: dark) {
            .stChatMessage {
                background-color: #2d2d2d;
                color: #ffffff !important;
            }
        }
        
        /* Streamlit dark mode overrides */
        @media (prefers-color-scheme: dark) {
            .stChatMessage[data-testid="chat-message-container-user"] {
                background-color: #1e1e1e;
                color: #ffffff !important;
            }
            .stChatMessage[data-testid="chat-message-container-assistant"] {
                background-color: #2d2d2d;
                color: #ffffff !important;
            }
            .stChatMessage p, .stChatMessage div, .stChatMessage span {
                color: #ffffff !important;
            }
        }
        
        /* Light mode chat message styling */
        @media (prefers-color-scheme: light) {
            .stChatMessage p, .stChatMessage div, .stChatMessage span {
                color: #262730 !important;
            }
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #1e3a5f;
        }
        
        /* Button styling */
        .stButton>button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Success message styling */
        .success-box {
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        /* Info message styling */
        .info-box {
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
        }
        
        /* Stats styling */
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin: 5px 0;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display and handle sidebar controls."""
    with st.sidebar:
        st.title("🎯 Interview Settings")
        
        # Role selection with custom option
        st.subheader("Select Role")
        
        # Add radio button for predefined vs custom role
        role_type = st.radio(
            "Choose role type:",
            ["Predefined Roles", "Custom Role"],
            key="role_type_selector"
        )
        
        if role_type == "Predefined Roles":
            selected_role = st.selectbox(
                "Choose the position you're interviewing for:",
                Config.get_roles(),
                key="role_selector"
            )
            custom_description = ""
        else:
            selected_role = st.text_input(
                "Enter your custom role:",
                placeholder="e.g., Senior Data Analyst, Marketing Manager",
                key="custom_role_input"
            )
            custom_description = st.text_area(
                "Enter job description and responsibilities:",
                placeholder="Describe the key responsibilities, required skills, and job description for this role...",
                key="custom_role_description",
                height=120
            )
        
        st.divider()
        
        # Start interview button
        if not st.session_state.interview_started:
            if st.button("🚀 Start Interview", type="primary", use_container_width=True):
                if role_type == "Custom Role":
                    if not selected_role.strip():
                        st.error("Please enter a custom role name.")
                        return
                    if not custom_description.strip():
                        st.error("Please enter a job description for the custom role.")
                        return
                    # Add custom role to the role list temporarily
                    enhanced_role = f"{selected_role} - {custom_description}"
                    start_interview(enhanced_role)
                else:
                    start_interview(selected_role)
        else:
            # Display session stats
            if st.session_state.interview_bot:
                stats = st.session_state.interview_bot.get_session_stats()
                
                st.subheader("📊 Session Stats")
                
                # Extract role name for display
                display_role = stats['role']
                if " - " in display_role:
                    display_role = display_role.split(" - ")[0]
                
                st.markdown(f"""
                    <div class="stat-card">
                        <h4>Current Role</h4>
                        <p style="font-size: 18px; margin: 0;">{display_role}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="stat-card">
                        <h4>Questions Asked</h4>
                        <p style="font-size: 24px; margin: 0; font-weight: bold;">{stats['questions_asked']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                if stats['elapsed_minutes'] is not None:
                    st.markdown(f"""
                        <div class="stat-card">
                            <h4>Time Elapsed</h4>
                            <p style="font-size: 24px; margin: 0; font-weight: bold;">{stats['elapsed_minutes']} min</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
            
            # Reset button
            if st.button("🔄 Reset Interview", type="secondary", use_container_width=True):
                reset_interview()
        
        st.divider()
        
        # Instructions
        with st.expander("📖 How to Use"):
            st.markdown("""
                1. **Select a role** from the dropdown above
                2. Click **Start Interview** to begin
                3. **Read each question** carefully
                4. **Type your answer** in the chat input
                5. **Receive feedback** and the next question
                6. Click **Reset** to start a new interview
                
                **Tips:**
                - Take your time to think through answers
                - Be specific and provide examples
                - Ask for clarification if needed
            """)


def start_interview(role: str):
    """
    Start a new interview session.
    
    Args:
        role: The selected job role
    """
    # Validate configuration
    is_valid, error_msg = Config.validate_config()
    if not is_valid:
        st.error(error_msg)
        return
    
    # Initialize the interview bot
    st.session_state.interview_bot = InterviewBot(
        api_key=Config.OPENAI_API_KEY,
        model_name=Config.MODEL_NAME,
        temperature=Config.TEMPERATURE
    )
    
    # Start the interview
    welcome_message = st.session_state.interview_bot.start_interview(role)
    
    # Update session state
    st.session_state.interview_started = True
    st.session_state.selected_role = role
    st.session_state.messages = [{"role": "assistant", "content": welcome_message}]
    st.session_state.awaiting_answer = True
    
    # Extract the first question from welcome message
    lines = welcome_message.split('\n')
    for i, line in enumerate(lines):
        if "Let's begin" in line and i + 1 < len(lines):
            st.session_state.current_question = '\n'.join(lines[i+1:]).strip()
            break
    
    st.rerun()


def reset_interview():
    """Reset the interview session."""
    if st.session_state.interview_bot:
        st.session_state.interview_bot.reset_session()
    
    st.session_state.interview_started = False
    st.session_state.current_question = ""
    st.session_state.messages = []
    st.session_state.selected_role = None
    st.session_state.awaiting_answer = False
    st.session_state.interview_bot = None
    
    st.rerun()


def display_chat_messages():
    """Display all chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input():
    """Handle user input and generate responses."""
    if prompt := st.chat_input("Type your answer here...", disabled=not st.session_state.interview_started):
        if not st.session_state.awaiting_answer:
            st.warning("Please wait for the next question.")
            return
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get evaluation and next question
        with st.chat_message("assistant"):
            with st.spinner("Evaluating your answer..."):
                result = st.session_state.interview_bot.evaluate_answer(
                    st.session_state.current_question,
                    prompt
                )
                
                feedback = result["feedback"]
                next_question = result["next_question"]
                
                # Display feedback
                st.markdown("### 📝 Feedback")
                st.markdown(feedback)
                
                st.divider()
                
                # Display next question
                st.markdown("### ❓ Next Question")
                st.markdown(next_question)
                
                # Combine for message history
                full_response = f"### 📝 Feedback\n\n{feedback}\n\n---\n\n### ❓ Next Question\n\n{next_question}"
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.session_state.current_question = next_question


def main():
    """Main function to run the Streamlit app."""
    # Page configuration
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon=Config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Display sidebar
    display_sidebar()
    
    # Main content area
    st.title(Config.APP_TITLE)
    st.markdown("### Practice your interview skills with AI-powered feedback")
    
    if not st.session_state.interview_started:
        # Welcome screen
        st.info("👈 Select a role from the sidebar and click 'Start Interview' to begin!")
        
        st.markdown("""
            ## Welcome to Your Mock Interview Practice! 🎯
            
            This AI-powered chatbot will help you prepare for your next job interview by:
            
            - 🎤 **Asking relevant questions** based on your selected role
            - 💡 **Providing constructive feedback** on your answers
            - 📈 **Progressively challenging you** with follow-up questions
            - ⏱️ **Tracking your progress** throughout the session
            
            ### Get Started:
            1. Choose your target role from the sidebar
            2. Click "Start Interview"
            3. Answer questions thoughtfully
            4. Learn from the feedback provided
            
            Good luck! 🍀
        """)
    else:
        # Display chat interface
        display_chat_messages()
        handle_user_input()


if __name__ == "__main__":
    main()

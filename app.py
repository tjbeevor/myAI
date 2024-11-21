import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
import time

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = 'gemini-pro'
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = datetime.now()

def check_session_timeout():
    """Check if the session has timed out"""
    if st.session_state.authenticated:
        timeout = 3600  # Default 1 hour
        if datetime.now() - st.session_state.last_activity > timedelta(seconds=timeout):
            st.session_state.authenticated = False
            st.session_state.login_attempts = 0
            return True
    return False

def authenticate(password_attempt):
    """Enhanced password authentication with attempt limiting"""
    max_attempts = 3
    correct_password = "password"  # In production, use st.secrets["APP_PASSWORD"]
    
    if st.session_state.login_attempts >= max_attempts:
        time.sleep(2)  # Add delay to prevent brute force
        return False
    
    st.session_state.login_attempts += 1
    if password_attempt == correct_password:
        st.session_state.login_attempts = 0
        st.session_state.last_activity = datetime.now()
        return True
    return False

def reset_chat():
    """Reset the chat history"""
    st.session_state.messages = []

def get_gemini_response(model_name, prompt):
    """Get response from the selected Gemini model"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def update_last_activity():
    """Update the timestamp of last activity"""
    st.session_state.last_activity = datetime.now()

def main():
    st.set_page_config(page_title="Secure Gemini Chatbot", layout="wide")
    
    # Configure Gemini with API key from secrets
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error("Error configuring Gemini API. Please check your API key in the secrets.")
        return
    
    # Initialize session state
    initialize_session_state()
    
    # Check for session timeout
    if check_session_timeout():
        st.warning("Your session has expired. Please log in again.")
        st.session_state.authenticated = False
    
    # Apply custom CSS
    st.markdown("""
        <style>
        .stTextInput {
            max-width: 400px;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .user-message {
            background-color: #e6f3ff;
        }
        .bot-message {
            background-color: #f0f2f6;
        }
        .stButton button {
            width: 100%;
            margin-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.title("🤖 Secure Gemini Chatbot")

    # Authentication section
    if not st.session_state.authenticated:
        st.markdown("### Authentication Required")
        password_input = st.text_input("Enter password:", type="password")
        
        # Show remaining attempts
        max_attempts = 3
        remaining_attempts = max_attempts - st.session_state.login_attempts
        if remaining_attempts < max_attempts:
            st.warning(f"Remaining attempts: {remaining_attempts}")
        
        if st.button("Login"):
            if authenticate(password_input):
                st.session_state.authenticated = True
                st.rerun()
            else:
                if remaining_attempts <= 1:
                    st.error("Maximum login attempts reached. Please try again later.")
                else:
                    st.error("Incorrect password!")
        return

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        model_options = [
            'gemini-pro',
            'gemini-pro-vision',
        ]
        selected_model = st.selectbox(
            "Select Gemini Model:",
            model_options,
            index=model_options.index(st.session_state.current_model)
        )
        
        if selected_model != st.session_state.current_model:
            st.session_state.current_model = selected_model
        
        if st.button("Reset Chat"):
            reset_chat()
            st.rerun()
        
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.login_attempts = 0
            st.rerun()
            
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
            This is a secure chatbot interface for Google's Gemini AI models.
            - Authenticated access only
            - Session timeout protection
            - Multiple model support
        """)

    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        with st.container():
            if role == "user":
                st.markdown(f"""
                    <div class="chat-message user-message">
                        <div><strong>You:</strong></div>
                        <div>{content}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message bot-message">
                        <div><strong>Assistant:</strong></div>
                        <div>{content}</div>
                    </div>
                """, unsafe_allow_html=True)

    # Chat input
    user_input = st.text_area("Your message:", key="user_input", height=100)
    if st.button("Send"):
        if user_input:
            update_last_activity()
            
            # Add user message to chat history
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Get bot response
            bot_response = get_gemini_response(st.session_state.current_model, user_input)
            
            # Add bot response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": bot_response,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # Clear input and rerun to update chat
            st.rerun()

if __name__ == "__main__":
    main()

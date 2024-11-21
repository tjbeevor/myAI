import streamlit as st
import google.generativeai as genai
from datetime import datetime

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_model' not in st.session_state:
        st.session_state.current_model = 'gemini-pro'

def authenticate(password_attempt):
    """Simple password authentication"""
    return password_attempt == "password"

def reset_chat():
    """Reset the chat history"""
    st.session_state.messages = []

def configure_gemini(api_key):
    """Configure the Gemini API with the provided key"""
    genai.configure(api_key=api_key)

def get_gemini_response(model_name, prompt):
    """Get response from the selected Gemini model"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.set_page_config(page_title="Secure Gemini Chatbot", layout="wide")
    
    # Initialize session state
    initialize_session_state()
    
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
        </style>
    """, unsafe_allow_html=True)

    # Title
    st.title("🤖 Secure Gemini Chatbot")

    # Authentication section
    if not st.session_state.authenticated:
        st.markdown("### Authentication Required")
        password_input = st.text_input("Enter password:", type="password")
        if st.button("Login"):
            if authenticate(password_input):
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Incorrect password!")
        return

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        api_key = st.text_input("Enter Gemini API Key:", type="password")
        
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
            st.experimental_rerun()
            
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
            This is a secure chatbot interface for Google's Gemini AI models.
            - Enter your API key
            - Select your preferred model
            - Start chatting!
        """)

    # Configure Gemini if API key is provided
    if api_key:
        configure_gemini(api_key)
    else:
        st.warning("Please enter your Gemini API key in the sidebar to continue.")
        return

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
            st.experimental_rerun()

if __name__ == "__main__":
    main()

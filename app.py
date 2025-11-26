#Load all the libraries
from dotenv import load_dotenv
from PIL import Image
import os
import streamlit as st
import google.generativeai as genai

# Page Config (Must be the first Streamlit command)
st.set_page_config(
    page_title="VisionTalk",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #e2e8f0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.9);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Chat Messages Container */
    .stChatMessage {
        background-color: transparent;
        border: none;
    }

    /* User Message Bubble (Targeted by Avatar) */
    [data-testid="stChatMessage"]:has(img[src*="1144760.png"]) {
        flex-direction: row-reverse;
        background-color: rgba(37, 99, 235, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(37, 99, 235, 0.3);
        border-radius: 20px 20px 0px 20px;
        padding: 15px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: right;
    }

    /* Align images in User Bubble to the right */
    [data-testid="stChatMessage"]:has(img[src*="1144760.png"]) [data-testid="stImage"] {
        display: flex;
        justify-content: flex-end;
    }

    /* Assistant Message Bubble (Targeted by Avatar) */
    [data-testid="stChatMessage"]:has(img[src*="6134346.png"]) {
        background-color: rgba(76, 29, 149, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(76, 29, 149, 0.3);
        border-radius: 20px 20px 20px 0px;
        padding: 15px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: left;
    }

    /* Avatar Styling */
    .stChatMessage .st-emotion-cache-1p1m4ay {
        background-color: transparent;
    }
    
    /* Header */
    .stAppHeader {
        background-color: transparent;
    }
    
    /* Input Area */
    .stChatInput {
        border-radius: 20px;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

#Configure Google API
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.warning("API Key not found. Please set the GOOGLE_API_KEY environment variable in your .env file.")
    st.stop()

genai.configure(api_key=api_key)

#Function to load Gemini model and generate response
def get_response(input_text, image_data):
    model = genai.GenerativeModel("gemini-2.0-flash")
    if input_text and image_data:
        response = model.generate_content([input_text, image_data])
    elif image_data:
        response = model.generate_content(image_data)
    elif input_text:
        response = model.generate_content(input_text)
    else:
        return "Please provide text or an image."
    return response.text

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.image("logo.png", width=200)
  # st.title("VisionTalk")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Image", use_container_width=True)
    
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main Chat Interface
st.header("Chat with VisionTalk 🤖")

# Define Avatars
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/1144/1144760.png" # Simple user icon
BOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/6134/6134346.png" # Robot icon

# Display Chat History
# Wrap in a container to isolate the chat messages for CSS selectors
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
        with st.chat_message(message["role"], avatar=avatar):
            if "image" in message and message["image"]:
                 st.image(message["image"], width=200)
            st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask something about the image..."):
    # Display User Message
    with chat_container: # Add new message to the container
        with st.chat_message("user", avatar=USER_AVATAR):
            if image:
                st.image(image, width=200)
            st.markdown(prompt)
    
    # Add to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "image": image if image else None
    })

    # Generate Response
    with chat_container: # Add response to the container
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            with st.spinner("Thinking..."):
                try:
                    response_text = get_response(prompt, image)
                    st.markdown(response_text)
                    
                    # Add to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text
                    })
                except Exception as e:
                    st.error(f"An error occurred: {e}")
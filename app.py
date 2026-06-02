import streamlit as st
from google import genai
from google.genai import types
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import os
import requests
import json
from pathlib import Path
import pandas as pd
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

# Check for Gemini API Key
if not os.getenv("GEMINI_API_KEY"):
    st.error("🔑 Gemini API Key not found! Please set GEMINI_API_KEY in your .env file or environment variables.")
    st.stop()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="MathBuddy: K-12 Math Tutor", page_icon="🧮")

# --- OAuth Configuration ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
MS_CLIENT_ID = os.getenv("MS_CLIENT_ID")
MS_CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8501")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_info"] = {}
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"
if "auth_error" not in st.session_state:
    st.session_state["auth_error"] = None
if "show_camera_input" not in st.session_state:
    st.session_state["show_camera_input"] = False

# --- Functional OAuth Callback Logic ---
if not st.session_state["authenticated"]:
    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        state = query_params.get("state")
        
        # Determine provider and exchange code for token
        if state == "google":
            token_url, user_url = "https://oauth2.googleapis.com/token", "https://www.googleapis.com/oauth2/v3/userinfo"
            creds = {"client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET}
            missing_creds = [name for name, value in {
                "GOOGLE_CLIENT_ID": GOOGLE_CLIENT_ID,
                "GOOGLE_CLIENT_SECRET": GOOGLE_CLIENT_SECRET,
            }.items() if not value]
        elif state == "microsoft":
            token_url, user_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token", "https://graph.microsoft.com/v1.0/me"
            creds = {"client_id": MS_CLIENT_ID, "client_secret": MS_CLIENT_SECRET}
            missing_creds = [name for name, value in {
                "MS_CLIENT_ID": MS_CLIENT_ID,
                "MS_CLIENT_SECRET": MS_CLIENT_SECRET,
            }.items() if not value]
        else:
            st.session_state["auth_error"] = "Unknown sign-in provider. Please try again from the login page."
            st.query_params.clear()
            st.rerun()

        if missing_creds:
            st.session_state["auth_error"] = f"{state.title()} sign-in is missing: {', '.join(missing_creds)}."
            st.query_params.clear()
            st.rerun()

        res = requests.post(token_url, data={**creds, "code": code, "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"})
        if res.status_code == 200:
            token = res.json().get("access_token")
            u_res = requests.get(user_url, headers={"Authorization": f"Bearer {token}"}).json()
            st.session_state["user_info"] = {"name": u_res.get("name") or u_res.get("displayName"), "email": u_res.get("email") or u_res.get("mail")}
            st.session_state["authenticated"] = True
            st.session_state["current_page"] = "dashboard"
            st.query_params.clear()
            st.rerun()
        else:
            error_details = res.json().get("error_description", "Please check your OAuth client ID, secret, and redirect URI.")
            st.session_state["auth_error"] = f"Sign-in failed: {error_details}"
            st.query_params.clear()
            st.rerun()

if not st.session_state["authenticated"]:
    st.title("🧮 Welcome to MathBuddy")
    st.write("Please sign in to access your patient, step-by-step AI math tutor.")

    if st.session_state.get("auth_error"):
        st.error(st.session_state["auth_error"])
        st.session_state["auth_error"] = None
    
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        google_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
            "client_id": GOOGLE_CLIENT_ID,
            "response_type": "code",
            "scope": "openid profile email",
            "redirect_uri": REDIRECT_URI,
            "state": "google",
        })
        st.link_button("🌐 Sign in with Google", google_url, use_container_width=True)
    else:
        st.warning("Google sign-in is not configured yet. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your .env file.")

    if MS_CLIENT_ID and MS_CLIENT_SECRET:
        ms_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?" + urlencode({
            "client_id": MS_CLIENT_ID,
            "response_type": "code",
            "scope": "User.Read",
            "redirect_uri": REDIRECT_URI,
            "state": "microsoft",
        })
        st.link_button("💻 Sign in with Microsoft", ms_url, use_container_width=True)
    st.stop()

# Initialize History & User Data
history = StreamlitChatMessageHistory(key="messages")
user_email = st.session_state["user_info"].get("email", "guest")
user_name = st.session_state["user_info"].get("name", "Student")

st.session_state["current_page"] = "dashboard"

st.title("🧮 MathBuddy Tutor Dashboard")
st.caption(f"Hello {user_name}! I'm here to help you discover answers step-by-step.")

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

grade = st.sidebar.selectbox(
    "Select your Grade Level:",
    ["Primary (Grades 1-5)", "Middle School (Grades 6-8)", "High School (Grades 9-12)"]
)

# Load or initialize progress data from file
PROGRESS_FILE = "progress_data.json"

def load_progress_data(email):
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            all_data = json.load(f)
            return all_data.get(email, [])
    return []

def save_progress_data(email, data):
    all_data = {}
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            all_data = json.load(f)
    all_data[email] = data
    with open(PROGRESS_FILE, "w") as f:
        json.dump(all_data, f, indent=2)

if "progress_data" not in st.session_state:
    st.session_state["progress_data"] = load_progress_data(user_email)

with st.sidebar.expander("📊 Log Today's Progress"):
    new_score = st.slider("Select your score:", 0, 100, 85)
    if st.button("Save Score"):
        lesson_num = len(st.session_state["progress_data"]) + 1
        st.session_state["progress_data"].append({"Lesson": f"L{lesson_num}", "Score": new_score})
        save_progress_data(user_email, st.session_state["progress_data"])
        st.success("✅ Score saved!")
        st.rerun()

if st.session_state["progress_data"]:
    st.sidebar.markdown("### 📈 Your Learning Curve")
    chart_df = pd.DataFrame(st.session_state["progress_data"]).set_index("Lesson")
    st.sidebar.line_chart(chart_df)

    csv_data = pd.DataFrame(st.session_state["progress_data"]).to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Progress CSV",
        data=csv_data,
        file_name="math_buddy_progress.csv",
        mime="text/csv",
        use_container_width=True
    )
else:
    st.sidebar.caption("No progress logged yet. Track your scores above!")

if st.sidebar.button("Clear Conversation History"):
    history.clear()
    st.rerun()

def get_system_prompt(grade_level):
    """Generate adaptive system prompt based on grade level."""
    base_rules = (
        "You are MathBuddy, a patient K-12 math tutor. "
        "NEVER give the final answer immediately. "
        "Instead, ask ONE guiding question first to help the student think through the problem. "
        "Only after they respond, show the next small step. "
        "Always format mathematical equations cleanly using LaTeX format wrapped in single dollar signs (e.g., $x^2 + y^2 = r^2$). "
        "Keep responses concise and encouraging."
    )
    
    if "Primary" in grade_level:
        return f"{base_rules} Use simple words, enthusiastic praise, and plenty of friendly emojis (like 🍎, ✨, 🚀). Keep explanations very short (2-3 sentences)."
    elif "Middle" in grade_level:
        return f"{base_rules} Use encouraging language, real-world examples (like sports or pizza), and clear, numbered steps."
    else:
        return f"{base_rules} Use mature, analytical reasoning. Focus on theorem validation, rigorous proofs, and deep conceptual understanding."

system_prompt = get_system_prompt(grade)

def show_gemini_error(error, action):
    """Display a helpful Gemini API error without exposing raw stack details."""
    message = str(error)
    if "quota" in message.lower() or "429" in message:
        st.error(
            "Gemini quota exceeded or rate limited. Please wait a bit and try again, "
            "or check your Google AI Studio quota."
        )
    else:
        st.error(f"Error {action}: {message}")

def history_to_gemini_contents(messages):
    contents = []
    for msg in messages:
        role = "model" if isinstance(msg, AIMessage) else "user"
        if isinstance(msg.content, list):
            text = next((item["text"] for item in msg.content if item.get("type") == "text"), "The user sent an image.")
        else:
            text = str(msg.content)
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    return contents

def send_text_query_to_llm(messages, system_prompt):
    """Send a text query to the LLM and return the response."""
    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=history_to_gemini_contents(messages),
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4,
            ),
        )
        return response.text
    except Exception as e:
        show_gemini_error(e, "calling Gemini")
        return None

def send_image_query_to_llm(image_bytes, mime_type, messages, system_prompt):
    """Send an image query to the LLM and return the response."""
    try:
        vision_message = HumanMessage(
            content=[
                {"type": "text", "text": "Please look at this handwritten math formula image. Convert it to standard LaTeX format and help me solve it step-by-step using your standard teaching rules."},
                {"type": "image", "mime_type": mime_type}
            ]
        )
        contents = history_to_gemini_contents(messages)
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(text=vision_message.content[0]["text"]),
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ],
            )
        )
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4,
            ),
        )
        return response.text, vision_message
    except Exception as e:
        show_gemini_error(e, "processing image")
        return None, None

for msg in history.messages:
    if isinstance(msg, HumanMessage):
        # Handle rendering text-only or complex multimodal text blocks cleanly in the history UI
        if isinstance(msg.content, list):
            text_content = next((item["text"] for item in msg.content if item["type"] == "text"), "Sent an image formula")
            st.chat_message("user").write(text_content)
        else:
            st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

st.markdown("---")
with st.expander("📷 Snap & Solve a Handwritten Formula"):
    st.caption("📸 Upload or take a photo of your handwritten math problem")
    if st.button("📷 Open camera", use_container_width=True):
        st.session_state["show_camera_input"] = True

    img_file = None
    if st.session_state["show_camera_input"]:
        img_file = st.camera_input("Take a photo of your math problem")

    uploaded_file = st.file_uploader("Or upload an image file", type=["png", "jpg", "jpeg"])
    
    active_file = img_file if img_file is not None else uploaded_file
    
    if active_file is not None:
        st.image(active_file, caption="Your Math Problem", use_container_width=True)
        if st.button("✨ Send to MathBuddy"):
            with st.spinner("🔍 Processing image with Gemini Vision..."):
                bytes_data = active_file.read()
                mime_type = active_file.type or "image/jpeg"
                response_content, vision_message = send_image_query_to_llm(bytes_data, mime_type, history.messages, system_prompt)
                
                if response_content:
                    history.add_message(vision_message)
                    history.add_ai_message(response_content)
                    st.rerun()

if user_query := st.chat_input("Ask your math question here..."):
    st.chat_message("user").write(user_query)
    history.add_user_message(user_query)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response_content = send_text_query_to_llm(history.messages, system_prompt)
            if response_content:
                st.write(response_content)
                history.add_ai_message(response_content)

if not history.messages and st.session_state["authenticated"]:
    st.info("👋 Welcome! Type a math question or upload an image to get started.")

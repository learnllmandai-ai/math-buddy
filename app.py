import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import os
import requests
import json
from pathlib import Path
import pandas as pd
import base64
from dotenv import load_dotenv

load_dotenv()

# Check for OpenAI API Key
if not os.getenv("OPENAI_API_KEY"):
    st.error("🔑 OpenAI API Key not found! Please set OPENAI_API_KEY in your .env file or environment variables.")
    st.stop()

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
        else:
            token_url, user_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token", "https://graph.microsoft.com/v1.0/me"
            creds = {"client_id": MS_CLIENT_ID, "client_secret": MS_CLIENT_SECRET}

        res = requests.post(token_url, data={**creds, "code": code, "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"})
        if res.status_code == 200:
            token = res.json().get("access_token")
            u_res = requests.get(user_url, headers={"Authorization": f"Bearer {token}"}).json()
            st.session_state["user_info"] = {"name": u_res.get("name") or u_res.get("displayName"), "email": u_res.get("email") or u_res.get("mail")}
            st.session_state["authenticated"] = True
            st.query_params.clear()
            st.rerun()

if not st.session_state["authenticated"]:
    st.title("🧮 Welcome to MathBuddy")
    st.write("Please sign in to access your patient, step-by-step AI math tutor.")
    
    google_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&response_type=code&scope=openid%20profile%20email&redirect_uri={REDIRECT_URI}&state=google"
    ms_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id={MS_CLIENT_ID}&response_type=code&scope=User.Read&redirect_uri={REDIRECT_URI}&state=microsoft"

    c1, c2 = st.columns(2)
    c1.link_button("🌐 Sign in with Google", google_url, use_container_width=True)
    c2.link_button("💻 Sign in with Microsoft", ms_url, use_container_width=True)
    st.stop()

# Initialize History & User Data
history = StreamlitChatMessageHistory(key="messages")
user_email = st.session_state["user_info"].get("email", "guest")
user_name = st.session_state["user_info"].get("name", "Student")

st.title("🧮 MathBuddy: K-12 Math Tutor")
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

def send_text_query_to_llm(messages, system_prompt):
    """Send a text query to the LLM and return the response."""
    try:
        full_chat_context = [SystemMessage(content=system_prompt)] + messages
        llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
        ai_response = llm.invoke(full_chat_context)
        return ai_response.content
    except Exception as e:
        st.error(f"❌ Error calling OpenAI: {str(e)}")
        return None

def send_image_query_to_llm(image_bytes, messages, system_prompt):
    """Send an image query to the LLM and return the response."""
    try:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        vision_message = HumanMessage(
            content=[
                {"type": "text", "text": "Please look at this handwritten math formula image. Convert it to standard LaTeX format and help me solve it step-by-step using your standard teaching rules."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        )
        full_chat_context = [SystemMessage(content=system_prompt)] + messages + [vision_message]
        llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
        ai_response = llm.invoke(full_chat_context)
        return ai_response.content, vision_message
    except Exception as e:
        st.error(f"❌ Error processing image: {str(e)}")
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
    img_file = st.camera_input("Take a photo of your math problem")
    uploaded_file = st.file_uploader("Or upload an image file", type=["png", "jpg", "jpeg"])
    
    active_file = img_file if img_file is not None else uploaded_file
    
    if active_file is not None:
        st.image(active_file, caption="Your Math Problem", use_container_width=True)
        if st.button("✨ Send to MathBuddy"):
            with st.spinner("🔍 Processing image with OpenAI Vision..."):
                bytes_data = active_file.read()
                response_content, vision_message = send_image_query_to_llm(bytes_data, history.messages, system_prompt)
                
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

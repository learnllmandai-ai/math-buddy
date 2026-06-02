import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
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

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🧮 Welcome to MathBuddy")
    st.write("Your patient, step-by-step K-12 math tutor powered by AI.")
    st.info("📚 Click below to get started. Your progress will be saved.")
    
    if st.button("✨ Continue to MathBuddy", use_container_width=True, type="primary"):
        st.session_state["authenticated"] = True
        st.rerun()
    st.stop()

st.title("🧮 MathBuddy: K-12 Math Tutor")
st.caption("A patient, encouraging tutor who helps you discover answers step-by-step!")

grade = st.sidebar.selectbox(
    "Select your Grade Level:",
    ["Primary (Grades 1-5)", "Middle School (Grades 6-8)", "High School (Grades 9-12)"]
)

# Load or initialize progress data from file
PROGRESS_FILE = "progress_data.json"

def load_progress_data():
    if Path(PROGRESS_FILE).exists():
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return []

def save_progress_data(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)

if "progress_data" not in st.session_state:
    st.session_state["progress_data"] = load_progress_data()

with st.sidebar.expander("📊 Log Today's Progress"):
    new_score = st.slider("Select your score:", 0, 100, 85)
    if st.button("Save Score"):
        lesson_num = len(st.session_state["progress_data"]) + 1
        st.session_state["progress_data"].append({"Lesson": f"L{lesson_num}", "Score": new_score})
        save_progress_data(st.session_state["progress_data"])
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
    st.session_state.messages = []
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

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
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
                response_content, vision_message = send_image_query_to_llm(bytes_data, st.session_state.messages, system_prompt)
                
                if response_content:
                    st.session_state.messages.append(vision_message)
                    st.session_state.messages.append(AIMessage(content=response_content))
                    st.rerun()

if user_query := st.chat_input("Ask your math question here..."):
    st.chat_message("user").write(user_query)
    st.session_state.messages.append(HumanMessage(content=user_query))
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response_content = send_text_query_to_llm(st.session_state.messages, system_prompt)
            if response_content:
                st.write(response_content)
                st.session_state.messages.append(AIMessage(content=response_content))

if not st.session_state.messages and st.session_state["authenticated"]:
    st.info("👋 Welcome! Type a math question or upload an image to get started.")

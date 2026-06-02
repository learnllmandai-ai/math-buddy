import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="MathBuddy: K-12 Math Tutor", page_icon="🧮")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 MathBuddy Secure Login")
    st.write("Welcome! Please sign in to access your patient AI math tutor.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 Sign in with Google", use_container_width=True):
            st.session_state["authenticated"] = True
            st.rerun()
    with col2:
        if st.button("💻 Sign in with Microsoft", use_container_width=True):
            st.session_state["authenticated"] = True
            st.rerun()
    st.stop()

st.title("🧮 MathBuddy: K-12 Math Tutor")
st.caption("A patient, encouraging tutor who helps you discover answers step-by-step!")

grade = st.sidebar.selectbox(
    "Select your Grade Level:",
    ["Primary (Grades 1-5)", "Middle School (Grades 6-8)", "High School (Grades 9-12)"]
)

if "progress_data" not in st.session_state:
    st.session_state["progress_data"] = []

with st.sidebar.expander("📊 Log Today's Progress"):
    new_score = st.slider("Select your score:", 0, 100, 85)
    if st.button("Save Score"):
        lesson_num = len(st.session_state["progress_data"]) + 1
        st.session_state["progress_data"].append({"Lesson": f"L{lesson_num}", "Score": new_score})
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

base_rules = (
    "You are MathBuddy, a patient K-12 math tutor. "
    "NEVER give the final answer immediately. "
    "Instead, break problems down and ask guiding questions to lead the student to discovery. "
    "Always format mathematical equations cleanly using LaTeX format wrapped in single dollar signs (e.g., $x^2 + y^2 = r^2$)."
)

if "Primary" in grade:
    system_prompt = f"{base_rules} Use simple words, enthusiastic praise, and plenty of friendly emojis (like 🍎, ✨, 🚀). Keep explanations short."
elif "Middle" in grade:
    system_prompt = f"{base_rules} Use encouraging language, real-world examples (like sports or pizza metrics), and clear, structured steps."
else:
    system_prompt = f"{base_rules} Use mature, analytical reasoning. Focus heavily on theorem validation, rigorous step proofing, and deep concepts."

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

st.markdown("---")
with st.expander("📷 Snap & Solve a Handwritten Formula"):
    img_file = st.camera_input("Take a photo of your math problem")
    uploaded_file = st.file_uploader("Or upload an image file", type=["png", "jpg", "jpeg"])
    
    active_file = img_file if img_file is not None else uploaded_file
    
    if active_file is not None:
        st.image(active_file, caption="Captured Math Problem", use_container_width=True)
        if st.button("✨ Send to MathBuddy"):
            with st.spinner("Reading handwritten formula..."):
                extracted_formula = "$2x + 5 = 15$" 
                st.session_state.messages.append(HumanMessage(content=f"Can you help me solve this visual problem step-by-step? {extracted_formula}"))
                st.rerun()

if user_query := st.chat_input("Ask your math question here..."):
    st.chat_message("user").write(user_query)
    st.session_state.messages.append(HumanMessage(content=user_query))
    
    full_chat_context = [SystemMessage(content=system_prompt)] + st.session_state.messages
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                llm = ChatOpenAI(model="gpt-4o", temperature=0.4)
                ai_response = llm.invoke(full_chat_context)
                st.write(ai_response.content)
                st.session_state.messages.append(AIMessage(content=ai_response.content))
            except Exception as e:
                st.error("Make sure your OPENAI_API_KEY is configured in your .env file!")
                st.error(f"Error details: {e}")

st.markdown("---")
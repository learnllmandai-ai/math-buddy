import base64
import hashlib
import os
import time
from datetime import date

from voice.text_to_speech import synthesize

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from langchain_core.messages import HumanMessage, AIMessage

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

load_dotenv()

st.set_page_config(page_title="ABACUS ELITE", layout="wide")

# --- Pre-loader Implementation ---
if "preloader_run" not in st.session_state:
    st.markdown("""
        <style>
            [data-testid="stSidebar"], section[data-testid="stSidebarNav"], .stAppHeader {
                display: none !important;
            }
            .loader-container {
                position: fixed;
                top: 0; left: 0; width: 100vw; height: 100vh;
                background: linear-gradient(-45deg, #1E1B4B, #2D1B69, #10B981, #0F172A);
                background-size: 400% 400%;
                animation: gradientBG 10s ease infinite;
                display: flex; justify-content: center; align-items: center;
                z-index: 999999; overflow: hidden; font-family: 'Inter', sans-serif;
            }
            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 24px; padding: 50px; text-align: center;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); width: 400px;
            }
            .main-icon { font-size: 90px; margin-bottom: 20px; animation: pulse 2s infinite; }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            .progress-bar-container { width: 100%; height: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 10px; margin: 25px 0; overflow: hidden; }
            .progress-fill { height: 100%; width: 0%; background: #FFFFFF; animation: loadProgress 3.5s forwards; }
            @keyframes loadProgress { 0% { width: 0%; } 100% { width: 100%; } }
            .status-text { color: white; font-weight: 500; font-size: 16px; }
            .status-text::after { content: ""; animation: rotatePhrases 3.5s infinite; }
            @keyframes rotatePhrases {
                0%, 30% { content: "🧮 Initializing ABACUS ELITE..."; }
                31%, 65% { content: "💎 Calibrating Soroban beads..."; }
                66%, 100% { content: "📈 Loading progress analytics..."; }
            }
        </style>
        <div class="loader-container">
            <div class="glass-card">
                <div class="main-icon">🧮</div>
                <div class="progress-bar-container"><div class="progress-fill"></div></div>
                <div class="status-text"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(3.5)
    st.session_state["preloader_run"] = True
    st.rerun()

# --- Deferred Imports ---
from analytics.mastery_tracker import compute_mastery, update_topic_mastery
from analytics.progress_tracker import summarize_progress
from analytics.reports import generate_report
from analytics.telemetry import log_interaction
from auth.auth_guard import initialize_auth, login_screen, logout, require_authentication
from gamification.badge_engine import earned_badges
from gamification.streak_tracker import current_streak, update_streak
from gamification.xp_manager import award_xp, total_xp
from multilingual.language_prompts import LANGUAGE_RULES
from multilingual.translator import translate_text
from tutoring.adaptive_engine import build_difficulty_rules, determine_difficulty
from tutoring.misconception_detector import detect_misconception
from tutoring.pedagogy_engine import enforce_pedagogy
from tutoring.tutor_chain import build_chain

# Initialize modern Google GenAI Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Helper Functions
def initials_from_name(name: str) -> str:
    parts = [part for part in str(name).split() if part]
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) >= 2 else (parts[0][:2].upper() if parts else "ST")

def avatar_palette(name: str):
    digest = hashlib.md5(str(name).encode("utf-8")).hexdigest()
    palette = [("#6366F1", "#22D3EE"), ("#8B5CF6", "#EC4899"), ("#10B981", "#22C55E")]
    return palette[int(digest[:2], 16) % len(palette)]

# --- Global Styling ---
st.markdown("""
    <style>
        .stApp { background-color: #0F172A; color: #E2E8F0; }
        [data-testid="stSidebar"] { background-color: #1E1B4B !important; border-right: 1px solid rgba(16, 185, 129, 0.2); }
        .abacus-container { background: #1E1B4B; border: 3px solid #2D1B69; border-radius: 20px; padding: 30px; display: flex; justify-content: center; position: relative; }
        .abacus-rod { width: 8px; height: 180px; background: #2D1B69; margin: 0 15px; position: relative; }
        .bead { width: 32px; height: 22px; border-radius: 11px; position: absolute; left: -12px; cursor: pointer; transition: transform 0.2s; }
        .bead-upper { background: rgba(255, 255, 255, 0.9); top: 10px; }
        .bead-lower { background: #10B981; box-shadow: 0 0 10px #10B981; }
        .bead-input { display: none; }
        .bead-input:checked + .bead-upper { transform: translateY(35px); }
        .bead-input:checked + .bead-lower { transform: translateY(-35px); }
    </style>
""", unsafe_allow_html=True)

initialize_auth()
if not require_authentication():
    login_screen()
    st.stop()

# --- Session States ---
for key, value in {
    "xp_total": 0, "streak_days": 0, "mastery_scores": {}, 
    "profile_pic": "car_profile.png", "messages": [], 
    "session_stats": {"questions": 0, "total_time": 0.0}, "daily_goal": 5
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 style='color:#10B981; font-size:2rem; margin:0;'>ABACUS ELITE</h1>", unsafe_allow_html=True)
    st.caption("Advanced Soroban Learning")
    
    st.markdown("### 📊 Dashboard")
    st.button("🏠 Dashboard", use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### Progress Charts")
    st.line_chart(pd.DataFrame({'Metrics': [30, 45, 40, 70, 85, 80, 95]}), height=120)
    
    language = st.selectbox("Language", ["English", "தமிழ்"])
    grade = st.selectbox("Grade", ["Grades 1-5", "Grades 6-8", "Grades 9-12"])

    if st.session_state.get("authenticated") and st.session_state.get("user_profile"):
        user_profile = st.session_state["user_profile"]
        profile_name = user_profile.get("name", "Student")
        initials = initials_from_name(profile_name)
        start_color, end_color = avatar_palette(profile_name)
        
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:12px; margin: 15px 0;">
                <div style="width:45px; height:45px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; background:linear-gradient(135deg, {start_color}, {end_color});">{initials}</div>
                <div><b>{profile_name}</b><br><span style="font-size:0.8rem; color:#bfdbfe;">Learner</span></div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", key="sidebar_logout", use_container_width=True):
            logout()

    st.sidebar.progress(min(st.session_state["session_stats"]["questions"] / st.session_state["daily_goal"], 1.0))
    st.sidebar.caption(f"{st.session_state['session_stats']['questions']} / {st.session_state['daily_goal']} questions answered")

    if st.sidebar.button("Clear Chat Context", use_container_width=True):
        st.session_state.messages = []
        st.session_state["session_stats"] = {"questions": 0, "total_time": 0.0}
        st.rerun()

# --- Main Interface Layout ---
col_practice, col_quiz = st.columns([2, 1], gap="large")

with col_practice:
    st.markdown("## PRACTICE MODE")
    
    # Generate Interactive Abacus HTML
    rods_html = ""
    for r in range(7):
        rod_content = '<div class="abacus-rod">'
        rod_content += f'<input type="checkbox" id="r{r}u" class="bead-input"><label for="r{r}u" class="bead bead-upper"></label>'
        for b in range(4):
            bottom_pos = 10 + (b * 25)
            rod_content += f'<input type="checkbox" id="r{r}l{b}" class="bead-input"><label for="r{r}l{b}" class="bead bead-lower" style="bottom:{bottom_pos}px"></label>'
        rod_content += '</div>'
        rods_html += rod_content

    st.markdown(f'<div class="abacus-container">{rods_html}</div>', unsafe_allow_html=True)
    st.button("✨ Start Practice Mode", use_container_width=True, type="primary")
    st.markdown("---")

    # Render Persistent Chat Logs
    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        st.chat_message(role).write(msg.content)

with col_quiz:
    st.markdown("## QUIZ MODE")
    with st.container(border=True):
        st.markdown('<div class="quiz-panel"><p>Current Challenge</p><h1>34 + 57 = ?</h1></div>', unsafe_allow_html=True)
        st.button("🚀 Take Quiz Now", use_container_width=True)

    st.metric("XP Total", st.session_state["xp_total"])

# --- Chat Handler Engine ---
student_question = st.chat_input("Ask a math question...")

if student_question:
    log_interaction(grade, student_question)
    st.session_state.messages.append(HumanMessage(content=student_question))
    
    override = enforce_pedagogy(student_question)
    if override:
        st.session_state.messages.append(AIMessage(content=override))
    else:
        mastery_scores = st.session_state.get("mastery_scores", {})
        mastery_score = sum(mastery_scores.values()) / len(mastery_scores) if mastery_scores else 0.0
        misconception = detect_misconception(student_question)
        
        st.session_state["xp_total"] += award_xp(True)
        st.session_state["mastery_scores"] = update_topic_mastery(st.session_state["mastery_scores"], misconception["topic"], 1, 1)

        try:
            start_time = time.time()
            chain = build_chain(grade)
            response = chain.invoke({"question": student_question, "history": st.session_state.messages[:-1]})
            explanation = response.content
            duration = time.time() - start_time
            
            if language == "தமிழ்":
                explanation = translate_text(explanation, "ta")
                
            st.session_state.messages.append(AIMessage(content=explanation))
            st.session_state["session_stats"]["questions"] += 1
            st.session_state["session_stats"]["total_time"] += duration
        except Exception as exc:
            st.error("Gemini context pipeline failure.")
            st.exception(exc)
    st.rerun()

# Audio TTS rendering out of the condition execution loop to ensure persistence
if st.session_state.messages and isinstance(st.session_state.messages[-1], AIMessage):
    if st.button("🔊 Listen to Latest Lesson"):
        with st.spinner("Generating natural audio track..."):
            try:
                audio_resp = synthesize(st.session_state.messages[-1].content)
                st.audio(audio_resp, format="audio/mp3", autoplay=True)
            except Exception as e:
                st.error(f"TTS Error: {e}")
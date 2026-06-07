import base64
import hashlib
import os
import time

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None

load_dotenv()

st.set_page_config(page_title="MathBuddy", layout="wide")

# --- Pre-loader Implementation ---
if "preloader_run" not in st.session_state:
    st.markdown("""
        <style>
            /* Hide Streamlit elements during loading */
            [data-testid="stSidebar"], section[data-testid="stSidebarNav"], .stAppHeader {
                display: none !important;
            }
            
            .loader-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: linear-gradient(-45deg, #4F46E5, #3B82F6, #10B981, #6366F1);
                background-size: 400% 400%;
                animation: gradientBG 10s ease infinite;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 999999;
                overflow: hidden;
                font-family: 'Inter', sans-serif;
            }

            @keyframes gradientBG {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .glass-card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 24px;
                padding: 50px;
                text-align: center;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
                width: 400px;
                position: relative;
                z-index: 10;
            }

            .main-icon {
                font-size: 80px;
                margin-bottom: 20px;
                display: inline-block;
                animation: pulse 2s ease-in-out infinite;
            }

            @keyframes pulse {
                0%, 100% { transform: scale(1); filter: drop-shadow(0 0 10px rgba(255,255,255,0.4)); }
                50% { transform: scale(1.1); filter: drop-shadow(0 0 25px rgba(255,255,255,0.7)); }
            }

            .progress-bar-container {
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                margin: 25px 0;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                width: 0%;
                background: #FFFFFF;
                box-shadow: 0 0 15px #FFFFFF;
                border-radius: 10px;
                animation: loadProgress 3.5s forwards cubic-bezier(0.4, 0, 0.2, 1);
            }

            @keyframes loadProgress {
                0% { width: 0%; }
                100% { width: 100%; }
            }

            .status-text {
                color: white;
                font-weight: 500;
                font-size: 16px;
                height: 20px;
            }

            .status-text::after {
                content: "";
                animation: rotatePhrases 3.5s infinite;
            }

            @keyframes rotatePhrases {
                0%, 30% { content: "🤖 Calling MathBuddy to the board..."; }
                31%, 65% { content: "✏️ Sharpening the virtual pencils..."; }
                66%, 100% { content: "💡 Pre-solving equations step-by-step..."; }
            }

            .math-particle {
                position: absolute;
                color: rgba(255, 255, 255, 0.3);
                font-size: 24px;
                user-select: none;
                pointer-events: none;
                animation: floatUp 4s infinite linear;
            }

            @keyframes floatUp {
                0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
                20% { opacity: 0.6; }
                80% { opacity: 0.6; }
                100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
            }
        </style>
        <div class="loader-container">
            <div class="math-particle" style="left:10%; animation-delay:0s;">+</div>
            <div class="math-particle" style="left:30%; animation-delay:1s;">÷</div>
            <div class="math-particle" style="left:50%; animation-delay:2s;">π</div>
            <div class="math-particle" style="left:70%; animation-delay:0.5s;">√</div>
            <div class="math-particle" style="left:90%; animation-delay:1.5s;">×</div>
            <div class="glass-card">
                <div class="main-icon">♾️</div>
                <div class="progress-bar-container"><div class="progress-fill"></div></div>
                <div class="status-text"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(3.5)
    st.session_state["preloader_run"] = True
    st.rerun()

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

# Initialize the modern Google GenAI Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


def initials_from_name(name: str) -> str:
    parts = [part for part in str(name).split() if part]
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][:2].upper() if parts else "ST"


def avatar_palette(name: str):
    digest = hashlib.md5(str(name).encode("utf-8")).hexdigest()
    palette = [
        ("#6366F1", "#22D3EE"),
        ("#8B5CF6", "#EC4899"),
        ("#10B981", "#22C55E"),
        ("#F59E0B", "#FB7185"),
        ("#0EA5E9", "#6366F1"),
    ]
    return palette[int(digest[:2], 16) % len(palette)]


def base64_image_data_uri(uploaded_file) -> str:
    image_bytes = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else b""
    if not image_bytes:
        raise ValueError("The uploaded image buffer is empty.")
    mime_type = getattr(uploaded_file, "type", "") or "image/png"
    return f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"


def run_vision_test(uploaded_file, grade: str) -> str:
    if uploaded_file is None:
        return "Please upload a handwritten formula image first."

    try:
        image_bytes = uploaded_file.getvalue()
        if not image_bytes:
            return "The image buffer is empty. Please try another capture or upload."

        image_uri = base64_image_data_uri(uploaded_file)
        prompt = (
            "You are MathBuddy's multimodal vision tutor. Parse the handwritten formula in the image "
            "and print the detected formula in exact single-dollar LaTeX formatting ($...$). "
            "Then provide a patient, step-by-step tutoring explanation for the student in the chat. "
            "Be concise, encouraging, and use plain language for the selected grade band "
            f"({grade})."
        )

        openai_key = os.environ.get("OPENAI_API_KEY")
        if OpenAI is not None and openai_key:
            try:
                openai_client = OpenAI(api_key=openai_key)
                response = openai_client.responses.create(
                    model="gpt-4o",
                    input=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": prompt},
                                {"type": "input_image", "image_url": image_uri},
                            ],
                        }
                    ],
                )
                return getattr(response, "output_text", None) or "Vision analysis completed."
            except Exception:
                pass

        mime_type = getattr(uploaded_file, "type", "") or "image/png"
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                prompt,
            ],
            config=types.GenerateContentConfig(temperature=0.2),
        )
        return getattr(response, "text", "") or "Vision analysis completed."
    except Exception as exc:
        return f"Vision test failed: {exc}"


initialize_auth()

if not require_authentication():
    login_screen()
    st.stop()

if "xp_total" not in st.session_state:
    st.session_state["xp_total"] = 0
if "streak_days" not in st.session_state:
    st.session_state["streak_days"] = 0
if "mastery_scores" not in st.session_state:
    st.session_state["mastery_scores"] = {}
if "profile_pic" not in st.session_state:
    st.session_state["profile_pic"] = "car_profile.png"

st.title("🧮 MathBuddy")

# Display user profile if authenticated
if st.session_state.get("authenticated") and st.session_state.get("user_profile"):
    user_profile = st.session_state["user_profile"]
    profile_name = user_profile.get("name", "Student")
    profile_picture = user_profile.get("picture", "")
    initials = initials_from_name(profile_name)
    start_color, end_color = avatar_palette(profile_name)

    custom_profile_pic = st.session_state.get("profile_pic")
    if custom_profile_pic and os.path.exists(custom_profile_pic):
        # Render custom image profile header
        col_img, col_txt = st.sidebar.columns([1, 2])
        with col_img:
            st.image(custom_profile_pic, width=100)
        with col_txt:
            st.markdown(
                f"""
                <div style="padding-top:10px;">
                  <div style="font-size:0.98rem; font-weight:700; color:#eff6ff;">{profile_name}</div>
                  <div style="font-size:0.82rem; color:#bfdbfe;">MathBuddy learner</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        # Fallback to initials badge
        st.sidebar.markdown(
            f"""
            <div style="position:sticky; top:0; z-index:10; padding:10px 4px 14px 4px; background:linear-gradient(180deg, rgba(15,23,42,0.96), rgba(15,23,42,0.86)); border-bottom:1px solid rgba(148,163,184,0.18); margin-bottom:10px;">
              <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:56px; height:56px; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; font-size:1rem; border:2px solid rgba(255,255,255,0.25); background:linear-gradient(135deg, {start_color}, {end_color}); box-shadow: 0 10px 24px rgba(99,102,241,0.35);">{initials}</div>
                <div>
                  <div style="font-size:0.98rem; font-weight:700; color:#eff6ff;">{profile_name}</div>
                  <div style="font-size:0.82rem; color:#bfdbfe;">MathBuddy learner</div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.sidebar.button("Logout", key="sidebar_logout"):
        logout()

# Existing sign-in info moved to the auth_guard
# st.caption(f"Signed in as: {st.session_state.get('auth_user', 'Student')}")

language = st.sidebar.selectbox("Language", ["English", "தமிழ்"])

grade = st.sidebar.selectbox(
    "Select Grade",
    ["Grades 1-5", "Grades 6-8", "Grades 9-12"],
)

with st.expander("📷 Snap & Solve a Handwritten Formula", expanded=True):
    uploaded_formula = st.file_uploader(
        "Upload or capture a handwritten formula", type=["png", "jpg", "jpeg", "webp"]
    )
    if uploaded_formula is not None:
        st.image(uploaded_formula, caption="Handwritten formula preview", use_container_width=True)
        image_bytes = uploaded_formula.getvalue()
        st.caption(f"Image buffer bytes: {len(image_bytes)}")

    if st.button("Run Vision Test Loop", key="vision_test_loop"):
        with st.spinner("Inspecting the handwriting with the multimodal vision tutor..."):
            explanation = run_vision_test(uploaded_formula, grade)
            st.chat_message("assistant").write(explanation)
            st.rerun()

progress_summary = summarize_progress()
mastery = st.session_state["mastery_scores"]

st.sidebar.metric("XP", st.session_state["xp_total"])
st.sidebar.metric("🔥 Streak", current_streak(st.session_state))
st.sidebar.write("Badges:", earned_badges(st.session_state["xp_total"]))

if mastery:
    st.sidebar.subheader("Mastery")
    for topic, score in mastery.items():
        st.sidebar.progress(score / 100)
        st.sidebar.caption(f"{topic}: {score}%")

st.sidebar.caption(LANGUAGE_RULES.get(language, LANGUAGE_RULES["English"]))

student_question = st.chat_input("Ask a math question...")

if student_question:
    log_interaction(grade, student_question)

    override = enforce_pedagogy(student_question)
    if override:
        st.chat_message("assistant").write(override)
    else:
        mastery_score = compute_mastery(1, 1)
        difficulty = determine_difficulty(mastery_score)
        difficulty_rules = build_difficulty_rules(mastery_score)
        misconception = detect_misconception(student_question)

        st.session_state["xp_total"] += award_xp(True)
        st.session_state["streak_days"] = current_streak(st.session_state) + 1
        st.session_state["mastery_scores"] = update_topic_mastery(
            st.session_state["mastery_scores"],
            misconception["topic"],
            1,
            1,
        )

        try:
            chain = build_chain(grade)
            response = chain.invoke({"question": student_question})
            explanation = response.content
        except Exception as exc:
            st.error("Unable to start the Gemini tutor right now.")
            st.info("Create or update your .env file with GEMINI_API_KEY=... and restart the app.")
            st.exception(exc)
            st.stop()
        if language == "தமிழ்":
            explanation = translate_text(explanation, "ta")

        st.caption(f"Difficulty: {difficulty} | {difficulty_rules}")
        st.caption(f"Misconception hint: {misconception['misconception']}")
        st.chat_message("assistant").write(explanation)

        if st.button("🔊 Listen to Lesson (Gemini)", key="tts_latest"):
            with st.spinner("Generating voice readback..."):
                try:
                    # Request Gemini to return the text spoken aloud as an audio file
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=f"Read the following educational math explanation out loud clearly and naturally. Do not say things like 'asterisk' or read raw symbols out loud, just speak naturally like a tutor: {explanation}",
                        config=types.GenerateContentConfig(
                            # Instruct the model to return raw audio bytes instead of text
                            response_mime_type="audio/mp3"
                        ),
                    )
                    
                    # Extract and play the raw audio part bytes natively in Streamlit
                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            st.audio(part.inline_data.data, format="audio/mp3", autoplay=True)
                except Exception as e:
                    st.error(f"Gemini Audio failed: {str(e)}")

        st.sidebar.metric("XP", st.session_state["xp_total"])
        st.sidebar.metric("🔥 Streak", current_streak(st.session_state))
        st.sidebar.write("Badges:", earned_badges(st.session_state["xp_total"]))

if st.sidebar.button("Generate Report"):
    import pandas as pd

    telemetry_df = pd.read_csv("data/telemetry.csv") if pd.io.common.file_exists("data/telemetry.csv") else pd.DataFrame()
    st.sidebar.json(generate_report("student", telemetry_df))

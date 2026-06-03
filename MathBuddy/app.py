import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

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

initialize_auth()

if not require_authentication():
    login_screen()
    st.stop()

st.set_page_config(page_title="MathBuddy", layout="wide")

if "xp_total" not in st.session_state:
    st.session_state["xp_total"] = 0
if "streak_days" not in st.session_state:
    st.session_state["streak_days"] = 0
if "mastery_scores" not in st.session_state:
    st.session_state["mastery_scores"] = {}

st.title("🧮 MathBuddy")
if st.sidebar.button("Sign out"):
    logout()
    st.rerun()

st.caption(f"Signed in as: {st.session_state.get('auth_user', 'Student')}")

language = st.sidebar.selectbox("Language", ["English", "தமிழ்"])

grade = st.sidebar.selectbox(
    "Select Grade",
    ["Grades 1-5", "Grades 6-8", "Grades 9-12"],
)

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

        st.sidebar.metric("XP", st.session_state["xp_total"])
        st.sidebar.metric("🔥 Streak", current_streak(st.session_state))
        st.sidebar.write("Badges:", earned_badges(st.session_state["xp_total"]))

if st.sidebar.button("Generate Report"):
    import pandas as pd

    telemetry_df = pd.read_csv("data/telemetry.csv") if pd.io.common.file_exists("data/telemetry.csv") else pd.DataFrame()
    st.sidebar.json(generate_report("student", telemetry_df))

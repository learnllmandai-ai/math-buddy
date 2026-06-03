import streamlit as st


def initialize_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False


def login_screen():
    st.markdown(
        """
        <h1 style='text-align:center'>
        🧮 MathBuddy
        </h1>
        <h4 style='text-align:center'>
        Adaptive K-12 AI Math Tutor
        </h4>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if st.button("🔵 Sign in with Google", use_container_width=True):
            st.session_state["authenticated"] = True

        if st.button("🟦 Sign in with Microsoft", use_container_width=True):
            st.session_state["authenticated"] = True


def require_authentication() -> bool:
    """Placeholder authentication guard."""
    return True

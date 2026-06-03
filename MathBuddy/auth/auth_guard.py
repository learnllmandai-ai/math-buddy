import streamlit as st


def initialize_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = ""


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

    st.caption("Sign in to continue to MathBuddy.")

    email = st.text_input("Email", placeholder="student@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter any password")

    if st.button("Sign in", use_container_width=True):
        if email.strip() and password.strip():
            st.session_state["authenticated"] = True
            st.session_state["auth_user"] = email.strip()
            st.rerun()
        else:
            st.warning("Please enter both email and password to sign in.")

    st.info("Demo login is enabled. Any non-empty email and password will sign you in.")


def logout():
    st.session_state["authenticated"] = False
    st.session_state["auth_user"] = ""


def require_authentication() -> bool:
    """Return whether the current session is authenticated."""
    return bool(st.session_state.get("authenticated", False))

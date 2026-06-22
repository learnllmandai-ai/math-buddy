import streamlit as st
import os
import requests
import urllib.parse


def initialize_auth():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "auth_user" not in st.session_state:
        st.session_state["auth_user"] = ""
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = {}
    if "student_id" not in st.session_state:
        st.session_state["student_id"] = ""
    if "last_login" not in st.session_state:
        st.session_state["last_login"] = ""


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

    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI") or "http://localhost:8501"

    if not google_client_id:
        st.error("Google Client ID is not configured. Please set GOOGLE_CLIENT_ID in your .env file.")
        st.stop()

    if "code" not in st.query_params:
        params = {
            "client_id": google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
        }
        auth_url = f"https://accounts.google.com/o/oauth2/auth?{urllib.parse.urlencode(params)}"
        st.link_button("Sign in with Google", auth_url, use_container_width=True)
    else:
        try:
            code = st.query_params["code"]
            google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

            if not google_client_secret:
                st.error("Google Client Secret is not configured. Please set GOOGLE_CLIENT_SECRET in your .env file.")
                st.stop()

            token_url = "https://oauth2.googleapis.com/token"
            token_payload = {
                "code": code,
                "client_id": google_client_id,
                "client_secret": google_client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
            token_response = requests.post(token_url, data=token_payload)
            token_response.raise_for_status()
            tokens = token_response.json()
            access_token = tokens["access_token"]

            userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            userinfo_response = requests.get(userinfo_url, headers={
                "Authorization": f"Bearer {access_token}"
            })
            userinfo_response.raise_for_status()
            user_profile = userinfo_response.json()

            st.session_state["authenticated"] = True
            st.session_state["auth_user"] = user_profile.get("email", "Unknown User")
            st.session_state["user_profile"] = {
                "name": user_profile.get("name", ""),
                "email": user_profile.get("email", ""),
                "picture": user_profile.get("picture", ""),
            }
            st.query_params.clear()
            st.rerun()

        except requests.exceptions.RequestException as e:
            st.error(f"Authentication error: {e}. Please try again.")
            st.session_state["authenticated"] = False
            st.session_state["auth_user"] = ""
            st.session_state["user_profile"] = {}
            st.query_params.clear()


def logout():
    st.session_state.clear()
    initialize_auth()
    st.rerun()


def require_authentication() -> bool:
    """Return whether the current session is authenticated."""
    return bool(st.session_state.get("authenticated", False))

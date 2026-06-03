"""Daily streak tracking helpers."""


def current_streak(session_state: dict) -> int:
    """Return the current daily streak from session state."""
    return int(session_state.get("streak_days", 0))


def update_streak(session_state: dict, student_id: str, last_login: str) -> dict:
    """Store simple streak info in session state."""
    session_state["student_id"] = student_id
    session_state["last_login"] = last_login
    session_state["streak_days"] = int(session_state.get("streak_days", 0)) + 1
    return session_state
